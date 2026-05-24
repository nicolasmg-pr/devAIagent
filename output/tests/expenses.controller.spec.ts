import { Test, TestingModule } from '@nestjs/testing';
import { ExpensesController } from '../src/expenses/expenses.controller';
import { ExpenseService } from '../src/expenses/expense.service';
import { CreateExpenseDto } from '../src/expenses/dto/create-expense.dto';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Expense } from '../src/expenses/expense.entity';
import { Repository } from 'typeorm';
import * as request from 'supertest';

describe('ExpensesController', () => {
  let controller: ExpensesController;
  let service: ExpenseService;
  let module: TestingModule;

  const mockExpense = {
    id: '1',
    amount: 100,
    date: '2023-10-01',
    description: 'Test',
    categoryId: 'cat1',
  };

  beforeEach(async () => {
    module = await Test.createTestingModule({
      controllers: [ExpensesController],
      providers: [
        ExpenseService,
        {
          provide: getRepositoryToken(Expense),
          useValue: {
            create: jest.fn().mockReturnValue(mockExpense),
            save: jest.fn().mockResolvedValue(mockExpense),
            find: jest.fn().mockResolvedValue([mockExpense]),
            findOne: jest.fn().mockResolvedValue(mockExpense),
            remove: jest.fn().mockResolvedValue(mockExpense),
          },
        },
      ],
    }).compile();

    controller = module.get<ExpensesController>(ExpensesController);
    service = module.get<ExpenseService>(ExpenseService);
  });

  describe('POST /api/v1/expenses', () => {
    it('should create an expense', async () => {
      const dto: CreateExpenseDto = {
        categoryId: 'cat1',
        amount: 100,
        date: '2023-10-01',
        description: 'Test',
      };

      const response = await request(module.getHttpServer())
        .post('/api/v1/expenses')
        .send(dto)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.amount).toBe(100);
    });
  });

  describe('GET /api/v1/expenses', () => {
    it('should return all expenses', async () => {
      const response = await request(module.getHttpServer())
        .get('/api/v1/expenses')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe('DELETE /api/v1/expenses/:id', () => {
    it('should delete an expense', async () => {
      const response = await request(module.getHttpServer())
        .delete('/api/v1/expenses/1')
        .expect(200);

      expect(response.body).toHaveProperty('id', '1');
    });
  });
});