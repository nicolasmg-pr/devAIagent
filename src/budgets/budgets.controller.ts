import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  UseGuards,
  Request,
} from '@nestjs/common';
import { BudgetsService } from './budgets.service';
import { CreateBudgetDto } from './dto/create-budget.dto';
import { UpdateBudgetDto } from './dto/update-budget.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('api/v1/budgets')
@UseGuards(JwtAuthGuard)
export class BudgetsController {
  constructor(private budgetsService: BudgetsService) {}

  @Post()
  async create(@Body() createBudgetDto: CreateBudgetDto, @Request() req) {
    const budget = await this.budgetsService.create(createBudgetDto, req.user.userId);
    return {
      id: budget.id,
      status: 'configured',
    };
  }

  @Get()
  async findAll(@Request() req) {
    return this.budgetsService.findAll(req.user.userId);
  }

  @Get(':id')
  async findOne(@Param('id') id: string, @Request() req) {
    return this.budgetsService.findOne(id, req.user.userId);
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateBudgetDto: UpdateBudgetDto,
    @Request() req,
  ) {
    await this.budgetsService.update(id, updateBudgetDto, req.user.userId);
    return {
      id,
      status: 'updated',
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @Request() req) {
    await this.budgetsService.remove(id, req.user.userId);
    return {
      id,
      status: 'deleted',
    };
  }

  @Get('status')
  async getBudgetStatus(@Request() req) {
    return this.budgetsService.getBudgetStatus(req.user.userId);
  }
}
