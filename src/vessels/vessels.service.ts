import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Vessel } from './entities/vessel.entity';
import { CreateVesselDto } from './dto/create-vessel.dto';

@Injectable()
export class VesselsService {
  constructor(
    @InjectRepository(Vessel)
    private vesselsRepository: Repository<Vessel>,
  ) {}

  async create(createVesselDto: CreateVesselDto): Promise<Vessel> {
    const vessel = this.vesselsRepository.create(createVesselDto);
    return this.vesselsRepository.save(vessel);
  }

  async findAll(): Promise<Vessel[]> {
    return this.vesselsRepository.find({
      relations: ['checklists'],
    });
  }

  async findOne(id: string): Promise<Vessel> {
    const vessel = await this.vesselsRepository.findOne({
      where: { id },
      relations: ['checklists'],
    });
    if (!vessel) {
      throw new NotFoundException(`Vessel with ID ${id} not found`);
    }
    return vessel;
  }

  async update(id: string, updateVesselDto: Partial<CreateVesselDto>): Promise<Vessel> {
    const vessel = await this.findOne(id);
    Object.assign(vessel, updateVesselDto);
    return this.vesselsRepository.save(vessel);
  }

  async remove(id: string): Promise<void> {
    const vessel = await this.findOne(id);
    await this.vesselsRepository.remove(vessel);
  }
}
