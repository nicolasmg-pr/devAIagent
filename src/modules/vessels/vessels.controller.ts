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
  BadRequestException,
  Req,
} from '@nestjs/common';
import { Request } from 'express';
import { VesselsService } from './vessels.service';
import { CreateVesselDto } from './dto/create-vessel.dto';

@Controller('vessels')
export class VesselsController {
  constructor(private readonly vesselsService: VesselsService) {}

  private getUserId(req: Request): string {
    return req.headers['x-user-id'] as string;
  }

  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async create(
    @Body() createVesselDto: CreateVesselDto,
    @Req() req: Request,
  ) {
    const userId = this.getUserId(req);
    if (!userId) {
      throw new BadRequestException('User ID is required');
    }
    return this.vesselsService.create(createVesselDto, userId);
  }

  @Get()
  async findAll(@Req() req: Request) {
    const userId = this.getUserId(req);
    if (!userId) {
      throw new BadRequestException('User ID is required');
    }
    return this.vesselsService.findAll(userId);
  }

  @Get(':id')
  async findOne(@Param('id') id: string, @Req() req: Request) {
    const userId = this.getUserId(req);
    return this.vesselsService.findOne(id, userId || undefined);
  }

  @Put(':id')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async update(
    @Param('id') id: string,
    @Body() updateVesselDto: CreateVesselDto,
    @Req() req: Request,
  ) {
    const userId = this.getUserId(req);
    if (!userId) {
      throw new BadRequestException('User ID is required');
    }
    return this.vesselsService.update(id, updateVesselDto, userId);
  }

  @Delete(':id')
  async remove(
    @Param('id') id: string,
    @Req() req: Request,
  ) {
    const userId = this.getUserId(req);
    if (!userId) {
      throw new BadRequestException('User ID is required');
    }
    await this.vesselsService.remove(id, userId);
    return { deleted: true, id };
  }
}