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
} from '@nestjs/common';
import { ProtocolsService } from './protocols.service';
import { CreateProtocolDto } from './dto/create-protocol.dto';

@Controller('protocols')
export class ProtocolsController {
  constructor(private readonly protocolsService: ProtocolsService) {}

  @Post()
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async create(@Body() createProtocolDto: CreateProtocolDto) {
    return this.protocolsService.create(createProtocolDto);
  }

  @Get()
  async findAll() {
    return this.protocolsService.findAll();
  }

  @Get('active')
  async getActive() {
    return this.protocolsService.getActiveProtocol();
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.protocolsService.findOne(id);
  }

  @Put(':id')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async update(
    @Param('id') id: string,
    @Body() updateProtocolDto: CreateProtocolDto,
  ) {
    return this.protocolsService.update(id, updateProtocolDto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    await this.protocolsService.remove(id);
    return { deleted: true, id };
  }
}