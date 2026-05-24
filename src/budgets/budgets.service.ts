import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Budget } from './entities/budget.entity';
import { CreateBudgetDto } from './dto/create-budget.dto';
import { UpdateBudgetDto } from './dto/update-budget.dto';

@Injectable()
export class BudgetsService {
  constructor(
    @InjectRepository(Budget)
    private budgetsRepository: Repository<Budget>,
  ) {}

  async create(createBudgetDto: CreateBudgetDto, userId: string): Promise<Budget> {
    const budget = this.budgetsRepository.create({
      ...createBudgetDto,
      user_id: userId,
      threshold_percent: createBudgetDto.threshold || 80.0,
    });
    return this.budgetsRepository.save(budget);
  }

  async findAll(userId: string): Promise<Budget[]> {
    return this.budgetsRepository.find({
      where: { user_id: userId },
      relations: ['category'],
      order: { year: 'DESC', month: 'DESC' },
    });
  }

  async findOne(id: string, userId: string): Promise<Budget> {
    const budget = await this.budgetsRepository.findOne({
      where: { id, user_id: userId },
      relations: ['category'],
    });
    if (!budget) {
      throw new NotFoundException(`Presupuesto con ID ${id} no encontrado`);
    }
    return budget;
  }

  async update(id: string, updateBudgetDto: UpdateBudgetDto, userId: string): Promise<Budget> {
    const budget = await this.findOne(id, userId);
    Object.assign(budget, updateBudgetDto);
    if (updateBudgetDto.threshold !== undefined) {
      budget.threshold_percent = updateBudgetDto.threshold;
    }
    return this.budgetsRepository.save(budget);
  }

  async remove(id: string, userId: string): Promise<void> {
    const budget = await this.findOne(id, userId);
    await this.budgetsRepository.remove(budget);
  }

  async getBudgetStatus(userId: string, month?: number, year?: number): Promise<any> {
    const currentMonth = month || new Date().getMonth() + 1;
    const currentYear = year || new Date().getFullYear();

    const budgets = await this.budgetsRepository
      .createQueryBuilder('budget')
      .leftJoinAndSelect('budget.category', 'category')
      .where('budget.user_id = :userId', { userId })
      .andWhere('budget.month = :month', { month: currentMonth })
      .andWhere('budget.year = :year', { year: currentYear })
      .getMany();

    const status = budgets.map((budget) => {
      const spent = budget.category.expenses.reduce(
        (sum, expense) => sum + expense.amount,
        0,
      );
      const percentage = (spent / budget.limit_amount) * 100;
      const alert = percentage >= budget.threshold_percent;

      return {
        id: budget.id,
        category: budget.category.name,
        limit: budget.limit_amount,
        spent,
        percentage: parseFloat(percentage.toFixed(2)),
        threshold: budget.threshold_percent,
        alert,
      };
    });

    return { month: currentMonth, year: currentYear, status };
  }
}
