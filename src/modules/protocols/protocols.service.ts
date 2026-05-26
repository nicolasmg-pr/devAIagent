import {
  Injectable,
  NotFoundException,
  ConflictException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Protocol } from '../../shared/entities/protocol.entity';
import { CreateProtocolDto } from './dto/create-protocol.dto';

@Injectable()
export class ProtocolsService {
  constructor(
    @InjectRepository(Protocol)
    private readonly protocolsRepository: Repository<Protocol>,
  ) {}

  async create(createProtocolDto: CreateProtocolDto): Promise<Protocol> {
    const existing = await this.protocolsRepository.findOne({
      where: { version: createProtocolDto.version },
    });

    if (existing) {
      throw new ConflictException(
        `Protocol version ${createProtocolDto.version} already exists`,
      );
    }

    const protocol = this.protocolsRepository.create({
      ...createProtocolDto,
      rules_payload: createProtocolDto.rules_payload || {},
      is_active: createProtocolDto.is_active ?? true,
    });

    return this.protocolsRepository.save(protocol);
  }

  async findAll(): Promise<Protocol[]> {
    return this.protocolsRepository.find({
      order: { created_at: 'DESC' },
    });
  }

  async findOne(id: string): Promise<Protocol> {
    const protocol = await this.protocolsRepository.findOne({
      where: { id },
    });

    if (!protocol) {
      throw new NotFoundException(
        `Protocol with ID ${id} not found`,
      );
    }

    return protocol;
  }

  async findByVersion(version: string): Promise<Protocol> {
    const protocol = await this.protocolsRepository.findOne({
      where: { version },
    });

    if (!protocol) {
      throw new NotFoundException(
        `Protocol version ${version} not found`,
      );
    }

    return protocol;
  }

  async getActiveProtocol(): Promise<Protocol | null> {
    return this.protocolsRepository.findOne({
      where: { is_active: true },
      order: { created_at: 'DESC' },
    });
  }

  async update(
    id: string,
    updateProtocolDto: Partial<CreateProtocolDto>,
  ): Promise<Protocol> {
    const protocol = await this.findOne(id);
    Object.assign(protocol, updateProtocolDto);
    return this.protocolsRepository.save(protocol);
  }

  async remove(id: string): Promise<void> {
    const protocol = await this.findOne(id);
    await this.protocolsRepository.remove(protocol);
  }
}