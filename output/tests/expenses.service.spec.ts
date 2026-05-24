import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ExpensesService } from './expenses.service';
import { Expense } from './entities/expense.entity';
import { CreateExpenseDto } from './dto/create-expense.dto';

describe('ExpensesService', () => {
  let service: ExpensesService;
  let repository: Repository<Expense>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ExpensesService,
        {
          provide: getRepositoryToken(Expense),
          useValue: {
            create: jest.fn(),
            save: jest.fn(),
            find: jest.fn(),
            findOne: jest.fn(),
            remove: jest.fn(),
            createQueryBuilder: jest.fn().mockReturnValue({
              where: jest.fn().mockReturnThis(),
              andWhere: jest.fn().mockReturnThis(),
              groupBy: jest.fn().mockReturnThis(),
              getRawMany: jest.fn(),
            }),
          },
        },
      ],
    }).compile();

    service = module.get<ExpensesService>(ExpensesService);
    repository = module.get<Repository<Expense>>(getRepositoryToken(Expense));
  });

  it('should create an expense', async () => {
    const createExpenseDto: CreateExpenseDto = {
      amount: 100,
      date: new Date(),
      description: 'Test',
      categoryId: '1',
    };
    const expense = { id: '1', ...createExpenseDto } as Expense;

    jest.spyOn(repository, 'save').mockResolvedValue(expense);

    const result = await service.create(createExpenseDto);
    expect(result).toEqual(expense);
    expect(repository.save).toHaveBeenCalled();
  });

  it('should return monthly statistics', async () => {
    const queryBuilderMock = {
      select: jest.fn().mockReturnThis(),
      where: jest.fn().mockReturnThis(),
      groupBy: jest.fn().mockReturnThis(),
      getRawMany: jest.fn().mockResolvedValue([{ total: 500 }]),
    };

    jest.spyOn(repository, 'createQueryBuilder').mockReturnValue(queryBuilderMock as any);

    const result = await service.getMonthlyStats(1, 2023);
    expect(result).toEqual([{ total: 500 }]);
  });
});