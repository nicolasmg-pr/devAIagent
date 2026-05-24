import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere } from 'typeorm';
import { Expense } from './entities/expense.entity';
import { CreateExpenseDto } from './dto/create-expense.dto';
import { UpdateExpenseDto } from './dto/update-expense.dto';

@Injectable()
export class ExpensesService {
  constructor(
    @InjectRepository(Expense)
    private expensesRepository: Repository<Expense>,
  ) {}

  async create(createExpenseDto: CreateExpenseDto, userId: string): Promise<Expense> {
    const expense = this.expensesRepository.create({
      ...createExpenseDto,
      user_id: userId,
    });
    return this.expensesRepository.save(expense);
  }

  async findAll(
    userId: string,
    filters?: {
      startDate?: string;
      endDate?: string;
      categoryId?: string;
      minAmount?: number;
      maxAmount?: number;
    },
  ): Promise<{ expenses: Expense[]; total: number; filters: object }> {
    const where: FindOptionsWhere<Expense> = { user_id: userId };

    if (filters?.categoryId) {
      where.category_id = filters.categoryId;
    }

    const queryBuilder = this.expensesRepository
      .createQueryBuilder('expense')
      .where(where);

    if (filters?.startDate) {
      queryBuilder.andWhere('expense.date >= :startDate', { startDate: filters.startDate });
    }
    if (filters?.endDate) {
      queryBuilder.andWhere('expense.date <= :endDate', { endDate: filters.endDate });
    }
    if (filters?.minAmount !== undefined) {
      queryBuilder.andWhere('expense.amount >= :minAmount', { minAmount: filters.minAmount });
    }
    if (filters?.maxAmount !== undefined) {
      queryBuilder.andWhere('expense.amount <= :maxAmount', { maxAmount: filters.maxAmount });
    }

    queryBuilder.orderBy('expense.date', 'DESC');

    const [expenses, total] = await queryBuilder.getManyAndCount();

    return {
      expenses,
      total,
      filters: filters || {},
    };
  }

  async findOne(id: string, userId: string): Promise<Expense> {
    const expense = await this.expensesRepository.findOne({
      where: { id, user_id: userId },
    });
    if (!expense) {
      throw new NotFoundException(`Gasto con ID ${id} no encontrado`);
    }
    return expense;
  }

  async update(id: string, updateExpenseDto: UpdateExpenseDto, userId: string): Promise<Expense> {
    const expense = await this.findOne(id, userId);
    Object.assign(expense, updateExpenseDto);
    return this.expensesRepository.save(expense);
  }

  async remove(id: string, userId: string): Promise<void> {
    const expense = await this.findOne(id, userId);
    await this.expensesRepository.remove(expense);
  }

  async getMonthlyStats(userId: string, month?: number, year?: number): Promise<any> {
    const currentMonth = month || new Date().getMonth() + 1;
    const currentYear = year || new Date().getFullYear();

    const result = await this.expensesRepository
      .createQueryBuilder('expense')
      .select('expense.category_id', 'category_id')
      .addSelect('c.name', 'category_name')
      .leftJoin('expense.category', 'c')
      .where('expense.user_id = :userId', { userId })
      .andWhere('EXTRACT(MONTH FROM expense.date) = :month', { month: currentMonth })
      .andWhere('EXTRACT(YEAR FROM expense.date) = :year', { year: currentYear })
      .addGroupBy('expense.category_id')
      .addGroupBy('c.name')
      .addSelect('SUM(expense.amount)', 'total')
      .getRawMany();

    const totalSpent = result.reduce((sum, row) => sum + parseFloat(row.sum), 0);

    return {
      totalSpent,
      breakdown: result.map((row) => ({
        category_id: row.category_id,
        category_name: row.category_name,
        total: parseFloat(row.total),
      })),
      month: currentMonth,
      year: currentYear,
    };
  }
}
