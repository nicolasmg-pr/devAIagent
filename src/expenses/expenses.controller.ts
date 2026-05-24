import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  Request,
} from '@nestjs/common';
import { ExpensesService } from './expenses.service';
import { CreateExpenseDto } from './dto/create-expense.dto';
import { UpdateExpenseDto } from './dto/update-expense.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('api/v1/expenses')
@UseGuards(JwtAuthGuard)
export class ExpensesController {
  constructor(private expensesService: ExpensesService) {}

  @Post()
  async create(@Body() createExpenseDto: CreateExpenseDto, @Request() req) {
    const expense = await this.expensesService.create(createExpenseDto, req.user.userId);
        return {
      data: expense,
      message: 'Expense created successfully',
    };
  }

  @Get()
  async findAll(
    @Request() req,
    @Query('startDate') startDate?: string,
    @Query('endDate') endDate?: string,
    @Query('categoryId') categoryId?: string,
    @Query('minAmount') minAmount?: number,
    @Query('maxAmount') maxAmount?: number,
  ) {
    const filters = {
      startDate,
      endDate,
      categoryId,
      minAmount: minAmount ? parseFloat(minAmount) : undefined,
      maxAmount: maxAmount ? parseFloat(maxAmount) : undefined,
    };
    return this.expensesService.findAll(req.user.userId, filters);
  }

  @Get(':id')
  async findOne(@Param('id') id: string, @Request() req) {
    return this.expensesService.findOne(id, req.user.userId);
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateExpenseDto: UpdateExpenseDto,
    @Request() req,
  ) {
    await this.expensesService.update(id, updateExpenseDto, req.user.userId);
    return {
      id,
      status: 'updated',
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @Request() req) {
    await this.expensesService.remove(id, req.user.userId);
    return {
      id,
      status: 'deleted',
    };
  }

  @Get('stats/monthly')
  async getMonthlyStats(
    @Request() req,
    @Query('month') month?: number,
    @Query('year') year?: number,
  ) {
    return this.expensesService.getMonthlyStats(req.user.userId, month, year);
  }
}
