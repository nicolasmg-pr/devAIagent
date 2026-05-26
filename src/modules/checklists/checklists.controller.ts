import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  UsePipes,
  ValidationPipe,
  Req,
  BadRequestException,
} from '@nestjs/common';
import { Request } from 'express';
import { ChecklistsService } from './checklists.service';
import { GenerateChecklistDto } from './dto/generate-checklist.dto';
import { UpdateChecklistItemDto } from './dto/update-item.dto';

@Controller('checklists')
export class ChecklistsController {
  constructor(
    private readonly checklistsService: ChecklistsService,
  ) {}

  private getUserId(req: Request): string {
    return req.headers['x-user-id'] as string;
  }

  @Post('generate')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async generate(
    @Body() generateDto: GenerateChecklistDto,
    @Req() req: Request,
  ) {
    return this.checklistsService.generate(generateDto);
  }

  @Get()
  async findAll(@Req() req: Request) {
    const userId = this.getUserId(req);
    return this.checklistsService.findAll(userId);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.checklistsService.findOne(id);
  }

  @Put(':id/items/:itemId')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async updateItemStatus(
    @Param('id') id: string,
    @Param('itemId') itemId: string,
    @Body() updateItemDto: UpdateChecklistItemDto,
  ) {
    return this.checklistsService.updateItemStatus(
      id,
      itemId,
      updateItemDto,
    );
  }

  @Post(':id/export')
  async exportChecklist(@Param('id') id: string) {
    return this.checklistsService.exportChecklist(id);
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    await this.checklistsService.remove(id);
    return { deleted: true, id };
  }
}