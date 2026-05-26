import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ChecklistInstance, ChecklistStatusEnum } from '../../shared/entities/checklist-instance.entity';
import { ChecklistItem } from '../../shared/entities/checklist-item.entity';
import { Vessel } from '../../shared/entities/vessel.entity';
import { Protocol } from '../../shared/entities/protocol.entity';
import { GenerateChecklistDto } from './dto/generate-checklist.dto';
import { UpdateChecklistItemDto } from './dto/update-item.dto';

@Injectable()
export class ChecklistsService {
  constructor(
    @InjectRepository(ChecklistInstance)
    private readonly checklistsRepository: Repository<ChecklistInstance>,
    @InjectRepository(ChecklistItem)
    private readonly itemsRepository: Repository<ChecklistItem>,
    @InjectRepository(Vessel)
    private readonly vesselsRepository: Repository<Vessel>,
    @InjectRepository(Protocol)
    private readonly protocolsRepository: Repository<Protocol>,
  ) {}

  async generate(dto: GenerateChecklistDto): Promise<{
    checklist_id: string;
    status: 'generated';
    estimated_items: number;
  }> {
    const vessel = await this.vesselsRepository.findOne({
      where: { id: dto.vessel_id },
    });

    if (!vessel) {
      throw new NotFoundException(
        `Vessel with ID ${dto.vessel_id} not found`,
      );
    }

    const protocol = await this.protocolsRepository.findOne({
      where: { version: dto.protocol_version },
    });

    if (!protocol) {
      throw new NotFoundException(
        `Protocol version ${dto.protocol_version} not found`,
      );
    }

    const checklist = this.checklistsRepository.create({
      vessel_id: vessel.id,
      protocol_id: protocol.id,
      status: ChecklistStatusEnum.PENDING,
    });

    const savedChecklist = await this.checklistsRepository.save(checklist);

    const items = this.generateItemsFromProtocol(
      vessel,
      protocol.rules_payload,
    );

    await this.itemsRepository.save(items);

    const updatedChecklist = await this.checklistsRepository.findOne({
      where: { id: savedChecklist.id },
      relations: ['items'],
    });

    return {
      checklist_id: updatedChecklist.id,
      status: 'generated',
      estimated_items: updatedChecklist.items.length,
    };
  }

  private generateItemsFromProtocol(
    vessel: Vessel,
    rulesPayload: Record<string, any>,
  ): ChecklistItem[] {
    const items: ChecklistItem[] = [];

    if (!rulesPayload || !rulesPayload.categories) {
      return items;
    }

    const categories = rulesPayload.categories;
    let itemCount = 1;

    for (const [category, rules] of Object.entries(categories)) {
      const ruleList = Array.isArray(rules) ? rules : [rules];

      for (const rule of ruleList as any[]) {
        const description = this.formatRuleDescription(rule, vessel);

        items.push(
          this.itemsRepository.create({
            rule_category: category,
            description,
            is_completed: false,
          }),
        );
        itemCount++;
      }
    }

    return items;
  }

  private formatRuleDescription(
    rule: any,
    vessel: Vessel,
  ): string {
    let description = rule.description || 'Check item';

    description = description.replace(
      '{vessel_name}',
      vessel.name,
    );
    description = description.replace(
      '{length}',
      vessel.length.toString(),
    );
    description = description.replace(
      '{capacity}',
      vessel.capacity.toString(),
    );
    description = description.replace(
      '{zone}',
      vessel.zone,
    );
    description = description.replace(
      '{propulsion}',
      vessel.propulsion,
    );

    return description;
  }

  async findAll(userId?: string): Promise<ChecklistInstance[]> {
    const where: Record<string, string> = {};
    if (userId) {
      where.user_id = userId;
    }

    return this.checklistsRepository.find({
      where,
      relations: ['vessel', 'protocol', 'items'],
      order: { created_at: 'DESC' },
    });
  }

  async findOne(id: string): Promise<ChecklistInstance> {
    const checklist = await this.checklistsRepository.findOne({
      where: { id },
      relations: ['vessel', 'protocol', 'items'],
    });

    if (!checklist) {
      throw new NotFoundException(
        `Checklist with ID ${id} not found`,
      );
    }

    return checklist;
  }

  async updateItemStatus(
    checklistId: string,
    itemId: string,
    updateItemDto: UpdateChecklistItemDto,
  ): Promise<{
    item_id: string;
    status: 'completed' | 'pending';
    updated_at: Date;
  }> {
    const checklist = await this.findOne(checklistId);

    const item = checklist.items.find((i) => i.id === itemId);

    if (!item) {
      throw new NotFoundException(
        `Item with ID ${itemId} not found in checklist ${checklistId}`,
      );
    }

    item.is_completed = updateItemDto.is_completed;
    item.last_updated = new Date();

    await this.itemsRepository.save(item);

    const allCompleted = checklist.items.every((i) => i.is_completed);
    if (allCompleted && checklist.status !== ChecklistStatusEnum.COMPLETED) {
      checklist.status = ChecklistStatusEnum.COMPLETED;
      await this.checklistsRepository.save(checklist);
    }

    return {
      item_id: item.id,
      status: item.is_completed ? 'completed' : 'pending',
      updated_at: item.last_updated,
    };
  }

  async exportChecklist(id: string): Promise<{
    export_ready: boolean;
    completion_percentage: number;
    template_data: any;
  }> {
    const checklist = await this.findOne(id);

    const totalItems = checklist.items.length;
    const completedItems = checklist.items.filter(
      (i) => i.is_completed,
    ).length;
    const completionPercentage =
      totalItems > 0
        ? Math.round((completedItems / totalItems) * 100)
        : 0;

    const exportReady =
      checklist.status === ChecklistStatusEnum.COMPLETED;

    const templateData = {
      checklist_id: checklist.id,
      vessel: {
        name: checklist.vessel?.name,
        length: checklist.vessel?.length,
        capacity: checklist.vessel?.capacity,
        zone: checklist.vessel?.zone,
        propulsion: checklist.vessel?.propulsion,
      },
      protocol: {
        version: checklist.protocol?.version,
        effective_date: checklist.protocol?.effective_date,
      },
      status: checklist.status,
      created_at: checklist.created_at,
      updated_at: checklist.updated_at,
      completion_percentage: completionPercentage,
      items: checklist.items.map((item) => ({
        category: item.rule_category,
        description: item.description,
        is_completed: item.is_completed,
        last_updated: item.last_updated,
      })),
    };

    return {
      export_ready: exportReady,
      completion_percentage: completionPercentage,
      template_data: templateData,
    };
  }

  async remove(id: string): Promise<void> {
    const checklist = await this.findOne(id);
    await this.checklistsRepository.remove(checklist);
  }
}