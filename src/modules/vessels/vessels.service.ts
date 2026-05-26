import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Vessel, ZoneEnum, PropulsionEnum } from '../../shared/entities/vessel.entity';
import { CreateVesselDto } from './dto/create-vessel.dto';

@Injectable()
export class VesselsService {
  constructor(
    @InjectRepository(Vessel)
    private readonly vesselsRepository: Repository<Vessel>,
  ) {}

  async create(
    createVesselDto: CreateVesselDto,
    userId: string,
  ): Promise<{ id: string; status: 'created' | 'updated' }> {
    const { name, length, capacity, zone, propulsion } = createVesselDto;

    const existingVessel = await this.vesselsRepository.findOne({
      where: { user_id: userId, name },
    });

    if (existingVessel) {
      existingVessel.length = length;
      existingVessel.capacity = capacity;
      existingVessel.zone = zone || existingVessel.zone;
      existingVessel.propulsion = propulsion || existingVessel.propulsion;
      await this.vesselsRepository.save(existingVessel);
      return { id: existingVessel.id, status: 'updated' };
    }

    const vessel = this.vesselsRepository.create({
      user_id: userId,
      name,
      length,
      capacity,
      zone: zone || ZoneEnum.COASTAL,
      propulsion: propulsion || PropulsionEnum.DIESEL,
    });

    const savedVessel = await this.vesselsRepository.save(vessel);
    return { id: savedVessel.id, status: 'created' };
  }

  async findAll(userId: string): Promise<Vessel[]> {
    return this.vesselsRepository.find({
      where: { user_id: userId },
      order: { created_at: 'DESC' },
    });
  }

  async findOne(id: string, userId?: string): Promise<Vessel> {
    const where: Record<string, string> = { id };
    if (userId) {
      where.user_id = userId;
    }

    const vessel = await this.vesselsRepository.findOne({
      where,
      relations: ['user'],
    });

    if (!vessel) {
      throw new NotFoundException(
        `Vessel with ID ${id} not found`,
      );
    }

    return vessel;
  }

  async update(
    id: string,
    updateVesselDto: CreateVesselDto,
    userId: string,
  ): Promise<Vessel> {
    const vessel = await this.findOne(id, userId);

    Object.assign(vessel, updateVesselDto);
    await this.vesselsRepository.save(vessel);

    return this.findOne(id, userId);
  }

  async remove(id: string, userId: string): Promise<void> {
    const vessel = await this.findOne(id, userId);
    await this.vesselsRepository.remove(vessel);
  }
}