import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Expense } from '../expenses/expense.entity';

@Injectable()
export class StatisticsService {
  constructor(
    @InjectRepository(Expense)
    private expensesRepo: Repository<Expense>,
  ) {}

  async getMonthlyStats(userId: string, month: number, year: number) {
    const start = new Date(year, month - 1, 1);
    const end = new Date(year, month, 0, 23, 59, 59);
    
    const result = await this.expensesRepo
      .createQueryBuilder('expense')
      .select('SUM(expense.amount)', 'total')
      .addSelect('category.name', 'category_name')
      .addSelect('SUM(expense.amount)', 'category_amount')
      .leftJoin('expense.category', 'category')
      .where('expense.user_id = :userId', { userId })
      .andWhere('expense.date BETWEEN :start AND :end', { start, end })
      .groupBy('category.name')
      .getRawMany();

    const total = result.reduce((sum, row) => sum + parseFloat(row.total || 0), 0);
    const byCategory = result.map(row => ({
      name: row.category_name,
      amount: parseFloat(row.category_amount || 0),
    }));

    return { total, byCategory };
  }
}