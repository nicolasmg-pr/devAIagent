import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Budget } from './budget.entity';
import { CreateBudgetDto } from './dto/create-budget.dto';
import { UpdateBudgetDto } from './dto/update-budget.dto';

@Injectable()
export class BudgetService {
  constructor(
    @InjectRepository(Budget)
    private budgetsRepo: Repository<Budget>,
  ) {}

  async create(dto: CreateBudgetDto, userId: string) {
    const budget = this.budgetsRepo.create({ ...dto, user_id: userId });
    return this.budgetsRepo.save(budget);
  }

  async findAll(userId: string) {
    return this.budgetsRepo.find({ where: { user_id: userId } });
  }

  async findOne(id: string, userId: string) {
    const budget = await this.budgetsRepo.findOne({ where: { id, user_id: userId } });
    if (!budget) throw new NotFoundException('Presupuesto no encontrado');
    return budget;
  }

  async update(id: string, dto: UpdateBudgetDto, userId: string) {
    const budget = await this.findOne(id, userId);
    Object.assign(budget, dto);
    return this.budgetsRepo.save(budget);
  }

  async remove(id: string, userId: string) {
    const budget = await this.findOne(id, userId);
    return this.budgetsRepo.remove(budget);
  }
}