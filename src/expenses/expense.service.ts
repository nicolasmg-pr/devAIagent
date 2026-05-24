import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Expense } from './expense.entity';
import { CreateExpenseDto } from './dto/create-expense.dto';
import { UpdateExpenseDto } from './dto/update-expense.dto';
import { QueryExpenseDto } from './dto/query-expense.dto';

@Injectable()
export class ExpenseService {
  constructor(
    @InjectRepository(Expense)
    private expensesRepo: Repository<Expense>,
  ) {}

  async create(dto: CreateExpenseDto, userId: string) {
    const expense = this.expensesRepo.create({ ...dto, user_id: userId });
    return this.expensesRepo.save(expense);
  }

  async findAll(query: QueryExpenseDto, userId: string) {
    const { page = 1, limit = 10, categoryId, startDate, endDate } = query;
    const where: any = { user_id: userId };
    if (categoryId) where.category_id = categoryId;
    if (startDate) where.date = `>= ${startDate}`;
    if (endDate) where.date = `<= ${endDate}`;
    
    const [data, total] = await this.expensesRepo.findAndCount({
      where,
      skip: (page - 1) * limit,
      take: limit,
      order: { date: 'DESC' },
    });
    return { data, total, page, limit };
  }

  async findOne(id: string, userId: string) {
    const expense = await this.expensesRepo.findOne({ where: { id, user_id: userId } });
    if (!expense) throw new NotFoundException('Gasto no encontrado');
    return expense;
  }

  async update(id: string, dto: UpdateExpenseDto, userId: string) {
    const expense = await this.findOne(id, userId);
    Object.assign(expense, dto);
    return this.expensesRepo.save(expense);
  }

  async remove(id: string, userId: string) {
    const expense = await this.findOne(id, userId);
    return this.expensesRepo.remove(expense);
  }
}