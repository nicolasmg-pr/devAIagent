import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Checklist } from './entities/checklist.entity';
import { ChecklistItem } from './entities/checklist-item.entity';
import { GenerateChecklistDto } from './dto/generate-checklist.dto';
import { UpdateItemDto } from './dto/update-item.dto';
import { ExportChecklistDto, ExportFormat } from './dto/export-checklist.dto';
import { VesselsService } from '../vessels/vessels.service';

@Injectable()
export class ChecklistsService {
  constructor(
    @InjectRepository(Checklist)
    private checklistsRepository: Repository<Checklist>,
    @InjectRepository(ChecklistItem)
    private checklistItemsRepository: Repository<ChecklistItem>,
    private vesselsService: VesselsService,
  ) {}

  async generateChecklist(dto: GenerateChecklistDto): Promise<Checklist> {
    const vessel = await this.vesselsService.findOne(dto.vessel_id);

    const checklist = this.checklistsRepository.create({
      vessel_id: vessel.id,
      vessel,
      generated_at: new Date(),
      status: 'IN_PROGRESS',
    });

    const items = this.generateChecklistItems(vessel, dto);
    const savedChecklist = await this.checklistsRepository.save(checklist);

    const checklistItems = items.map((item) =>
      this.checklistItemsRepository.create({
        ...item,
        checklist_id: savedChecklist.id,
        checklist: savedChecklist,
      }),
    );

    await this.checklistItemsRepository.save(checklistItems);

    return this.findOne(savedChecklist.id);
  }

  private generateChecklistItems(vessel, dto: GenerateChecklistDto): Partial<ChecklistItem>[] {
    const items: Partial<ChecklistItem>[] = [];

    // General safety items
    items.push({
      section: 'General Safety',
      description: 'Life jackets available for all passengers',
      is_completed: false,
      custom_notes: '',
      rule_trigger_id: null,
    });

    items.push({
      section: 'General Safety',
      description: 'First aid kit on board',
      is_completed: false,
      custom_notes: '',
      rule_trigger_id: null,
    });

    items.push({
      section: 'Navigation',
      description: 'Charts and navigation equipment ready',
      is_completed: false,
      custom_notes: '',
      rule_trigger_id: null,
    });

    // Zone-specific items
    if (vessel.navigation_zone === 'COASTAL') {
      items.push({
        section: 'Zone Requirements',
        description: 'Distress signals for coastal navigation',
        is_completed: false,
        custom_notes: '',
        rule_trigger_id: null,
      });
    }

    // Length-specific items
    if (vessel.length > 12) {
      items.push({
        section: 'Length Requirements',
        description: 'Anchor line and backup anchor prepared',
        is_completed: false,
        custom_notes: '',
        rule_trigger_id: null,
      });
    }

    // Passenger-specific items
    if (dto.passenger_count && dto.passenger_count > 10) {
      items.push({
        section: 'Passenger Safety',
        description: 'Emergency evacuation plan reviewed',
        is_completed: false,
        custom_notes: '',
        rule_trigger_id: null,
      });
    }

    return items;
  }

  async findAll(): Promise<Checklist[]> {
    return this.checklistsRepository.find({
      relations: ['vessel', 'items'],
    });
  }

  async findOne(id: string): Promise<Checklist> {
    const checklist = await this.checklistsRepository.findOne({
      where: { id },
      relations: ['vessel', 'items'],
    });
    if (!checklist) {
      throw new NotFoundException(`Checklist with ID ${id} not found`);
    }
    return checklist;
  }

  async updateItems(
    checklistId: string,
    updates: UpdateItemDto[],
  ): Promise<Checklist> {
    const checklist = await this.findOne(checklistId);

    for (const update of updates) {
      const item = checklist.items.find((i) => i.id === update.item_id);
      if (item) {
        item.is_completed = update.is_completed;
        if (update.custom_notes !== undefined) {
          item.custom_notes = update.custom_notes;
        }
      }
    }

    const allCompleted = checklist.items.every((item) => item.is_completed);
    if (allCompleted) {
      checklist.status = 'COMPLETED';
    }

    await this.checklistsRepository.save(checklist);
    return this.findOne(checklistId);
  }

  async exportChecklist(
    checklistId: string,
    dto: ExportChecklistDto,
  ): Promise<{ url: string; content?: string; metadata: any }> {
    const checklist = await this.findOne(checklistId);

    let content: string;
    let url: string;

    if (dto.format === ExportFormat.TEXT) {
      content = this.generateTextContent(checklist, dto.include_timestamp);
      url = `s3://checklist-exports/${checklistId}.txt`;
    } else {
      content = this.generatePdfContent(checklist, dto.include_timestamp);
      url = `s3://checklist-exports/${checklistId}.pdf`;
    }

    checklist.export_reference = url;
    await this.checklistsRepository.save(checklist);

    const metadata = {
      checklist_id: checklistId,
      format: dto.format,
      generated_at: new Date().toISOString(),
      vessel_name: checklist.vessel.type,
      items_count: checklist.items.length,
      completed_items: checklist.items.filter((i) => i.is_completed).length,
    };

    return { url, content, metadata };
  }

  private generateTextContent(checklist: Checklist, includeTimestamp: boolean): string {
    let text = `MARITIME PRE-SAILING CHECKLIST\n`;
    text += `Vessel: ${checklist.vessel.type}\n`;
    text += `Zone: ${checklist.vessel.navigation_zone}\n`;
    if (includeTimestamp) {
      text += `Generated: ${checklist.generated_at.toISOString()}\n`;
    }
    text += `Status: ${checklist.status}\n\n`;

    const sections = new Set(checklist.items.map((item) => item.section));
    sections.forEach((section) => {
      text += `=== ${section} ===\n`;
      const sectionItems = checklist.items.filter((item) => item.section === section);
      sectionItems.forEach((item) => {
        const status = item.is_completed ? '[X]' : '[ ]';
        text += `${status} ${item.description}\n`;
        if (item.custom_notes) {
          text += `    Notes: ${item.custom_notes}\n`;
        }
      });
      text += '\n';
    });

    return text;
  }

  private generatePdfContent(
    checklist: Checklist,
    includeTimestamp: boolean,
  ): string {
    const textContent = this.generateTextContent(checklist, includeTimestamp);
    return `PDF_BASE64_ENCODED_CONTENT_${checklist.id}`;
  }

  async remove(id: string): Promise<void> {
    const checklist = await this.findOne(id);
    await this.checklistsRepository.remove(checklist);
  }
}
