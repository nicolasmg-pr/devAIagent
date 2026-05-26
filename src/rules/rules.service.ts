import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RuleTemplate } from './entities/rule-template.entity';

@Injectable()
export class RulesService {
  constructor(
    @InjectRepository(RuleTemplate)
    private rulesRepository: Repository<RuleTemplate>,
  ) {}

  async findAll(): Promise<RuleTemplate[]> {
    return this.rulesRepository.find();
  }

  async findOne(id: string): Promise<RuleTemplate> {
    const rule = await this.rulesRepository.findOne({ where: { id } });
    if (!rule) {
      throw new NotFoundException(`Rule template with ID ${id} not found`);
    }
    return rule;
  }

  async findByZone(zoneCode: string): Promise<RuleTemplate[]> {
    return this.rulesRepository.find({
      where: {
        category: 'ZONE',
        condition_expression: {
          navigation_zone: zoneCode,
        } as any,
      },
    });
  }

  async findByLength(maxLength: number): Promise<RuleTemplate[]> {
    return this.rulesRepository.find({
      where: {
        category: 'LENGTH',
        condition_expression: {
          max_length: maxLength,
        } as any,
      },
    });
  }

  async create(ruleData: Partial<RuleTemplate>): Promise<RuleTemplate> {
    const rule = this.rulesRepository.create(ruleData);
    return this.rulesRepository.save(rule);
  }

  async update(id: string, ruleData: Partial<RuleTemplate>): Promise<RuleTemplate> {
    const rule = await this.findOne(id);
    Object.assign(rule, ruleData);
    return this.rulesRepository.save(rule);
  }

  async remove(id: string): Promise<void> {
    const rule = await this.findOne(id);
    await this.rulesRepository.remove(rule);
  }
}
