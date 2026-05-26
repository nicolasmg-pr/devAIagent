import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Patch,
  Delete,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ChecklistsService } from './checklists.service';
import { GenerateChecklistDto } from './dto/generate-checklist.dto';
import { UpdateItemDto } from './dto/update-item.dto';
import { ExportChecklistDto } from './dto/export-checklist.dto';
import { Checklist } from './entities/checklist.entity';

@ApiTags('checklists')
@Controller('api/v1/checklists')
export class ChecklistsController {
  constructor(private readonly checklistsService: ChecklistsService) {}

  @Post('generate')
  @ApiOperation({ summary: 'Generate customized pre-sailing checklist' })
  @ApiResponse({ status: 201, description: 'Checklist generated successfully', type: Checklist })
  async generate(@Body() dto: GenerateChecklistDto): Promise<Checklist> {
    return this.checklistsService.generateChecklist(dto);
  }

  @Get()
  @ApiOperation({ summary: 'Retrieve all checklists' })
  @ApiResponse({ status: 200, description: 'Return all checklists', type: [Checklist] })
  async findAll(): Promise<Checklist[]> {
    return this.checklistsService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Fetch checklist state with completion status' })
  @ApiResponse({ status: 200, description: 'Return checklist by ID', type: Checklist })
  @ApiResponse({ status: 404, description: 'Checklist not found' })
  async findOne(@Param('id') id: string): Promise<Checklist> {
    return this.checklistsService.findOne(id);
  }

  @Patch(':id/items')
  @ApiOperation({ summary: 'Update item completion toggle and notes' })
  @ApiResponse({ status: 200, description: 'Items updated successfully', type: Checklist })
  @ApiResponse({ status: 404, description: 'Checklist not found' })
  async updateItems(
    @Param('id') id: string,
    @Body() updates: UpdateItemDto[],
  ): Promise<Checklist> {
    return this.checklistsService.updateItems(id, updates);
  }

  @Post(':id/export')
  @ApiOperation({ summary: 'Export checklist as PDF or text' })
  @ApiResponse({ status: 200, description: 'Export generated successfully' })
  @ApiResponse({ status: 404, description: 'Checklist not found' })
  async export(
    @Param('id') id: string,
    @Body() dto: ExportChecklistDto,
  ): Promise<{ url: string; content?: string; metadata: any }> {
    return this.checklistsService.exportChecklist(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete a checklist' })
  @ApiResponse({ status: 204, description: 'Checklist deleted successfully' })
  @ApiResponse({ status: 404, description: 'Checklist not found' })
  async remove(@Param('id') id: string): Promise<void> {
    return this.checklistsService.remove(id);
  }
}
