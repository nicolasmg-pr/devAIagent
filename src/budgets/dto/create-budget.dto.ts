import { IsNumber, IsOptional, IsUUID } from 'class-validator';

export class CreateBudgetDto {
  @IsUUID()
  categoryId: string;

  @IsNumber()
  monthlyLimit: number;

  @IsNumber()
  @IsOptional()
  alertThreshold?: number = 80;
}