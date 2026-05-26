import { IsEnum, IsBoolean, IsOptional } from 'class-validator';

export enum ExportFormat {
  PDF = 'pdf',
  TEXT = 'text',
}

export class ExportChecklistDto {
  @IsEnum(ExportFormat, {
    message: 'Format must be either pdf or text',
  })
  format: ExportFormat;

  @IsBoolean()
  @IsOptional()
  include_timestamp?: boolean = true;
}
