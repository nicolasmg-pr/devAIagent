import { IsNumber, IsOptional, IsUUID } from 'class-validator';

export class UpdateBudgetDto {
  @IsUUID()
  @IsOptional()
  categoryId?: string;

  @IsNumber()
  @IsOptional()
  monthlyLimit?: number;

  @IsNumber()
  @IsOptional()
  alertThreshold?: number;
}