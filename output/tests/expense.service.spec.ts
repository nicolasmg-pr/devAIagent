import { Test, TestingModule } from '@nestjs/testing';
import { ExpenseService } from '../src/expenses/expense.service';
import { Expense } from '../src/expenses/expense.entity';
import { CreateExpenseDto } from '../src/expenses/dto/create-expense.dto';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

describe('ExpenseService', () => {
  let service: ExpenseService;
  let repository: Repository<Expense>;

  const mockExpense = {
    id: '1',
    amount: 100,
    date: '2023-10-01',
    description: 'Test',
    categoryId: 'cat1',
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
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

    service = module.get<ExpenseService>(ExpenseService);
    repository = module.get<Repository<Expense>>(getRepositoryToken(Expense));
  });

  it('should create an expense', async () => {
    const dto: CreateExpenseDto = {
      categoryId: 'cat1',
      amount: 100,
      date: '2023-10-01',
      description: 'Test',
    };

    const result = await service.create(dto);

    expect(repository.save).toHaveBeenCalledWith(expect.objectContaining(dto));
    expect(result).toEqual(mockExpense);
  });

  it('should return all expenses', async () => {
    const result = await service.findAll();

    expect(repository.find).toHaveBeenCalled();
    expect(result).toEqual([mockExpense]);
  });

  it('should remove an expense', async () => {
    const id = '1';
    const result = await service.remove(id);

    expect(repository.remove).toHaveBeenCalledWith(mockExpense);
    expect(result).toEqual(mockExpense);
  });
});