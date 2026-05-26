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
  Query,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { RulesService } from './rules.service';
import { RuleTemplate } from './entities/rule-template.entity';

@ApiTags('rules')
@Controller('api/v1/rules')
export class RulesController {
  constructor(private readonly rulesService: RulesService) {}

  @Get()
  @ApiOperation({ summary: 'Retrieve all rule templates' })
  @ApiResponse({ status: 200, description: 'Return all rule templates', type: [RuleTemplate] })
  async findAll(): Promise<RuleTemplate[]> {
    return this.rulesService.findAll();
  }

  @Get('zone/:code')
  @ApiOperation({ summary: 'Retrieve zone-specific maritime safety regulations' })
  @ApiResponse({ status: 200, description: 'Return zone-specific rules' })
  async findByZone(@Param('code') code: string): Promise<RuleTemplate[]> {
    return this.rulesService.findByZone(code);
  }

  @Get('length/:meters')
  @ApiOperation({ summary: 'Retrieve length-specific equipment calculations' })
  @ApiResponse({ status: 200, description: 'Return length-based rules' })
  async findByLength(@Param('meters') meters: number): Promise<RuleTemplate[]> {
    return this.rulesService.findByLength(meters);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Retrieve rule template by ID' })
  @ApiResponse({ status: 200, description: 'Return rule template by ID' })
  @ApiResponse({ status: 404, description: 'Rule template not found' })
  async findOne(@Param('id') id: string): Promise<RuleTemplate> {
    return this.rulesService.findOne(id);
  }

  @Post()
  @ApiOperation({ summary: 'Create a new rule template' })
  @ApiResponse({ status: 201, description: 'Rule template created' })
  async create(@Body() ruleData: Partial<RuleTemplate>): Promise<RuleTemplate> {
    return this.rulesService.create(ruleData);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update a rule template' })
  @ApiResponse({ status: 200, description: 'Rule template updated' })
  async update(
    @Param('id') id: string,
    @Body() ruleData: Partial<RuleTemplate>,
  ): Promise<RuleTemplate> {
    return this.rulesService.update(id, ruleData);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete a rule template' })
  @ApiResponse({ status: 204, description: 'Rule template deleted' })
  async remove(@Param('id') id: string): Promise<void> {
    return this.rulesService.remove(id);
  }
}
