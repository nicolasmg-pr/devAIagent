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
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { VesselsService } from './vessels.service';
import { CreateVesselDto } from './dto/create-vessel.dto';
import { Vessel } from './entities/vessel.entity';

@ApiTags('vessels')
@Controller('api/v1/vessels')
export class VesselsController {
  constructor(private readonly vesselsService: VesselsService) {}

  @Post()
  @ApiOperation({ summary: 'Create or update boat specifications' })
  @ApiResponse({ status: 201, description: 'Vessel created successfully', type: Vessel })
  @ApiResponse({ status: 400, description: 'Bad request' })
  async create(@Body() createVesselDto: CreateVesselDto): Promise<Vessel> {
    return this.vesselsService.create(createVesselDto);
  }

  @Get()
  @ApiOperation({ summary: 'Retrieve all vessels' })
  @ApiResponse({ status: 200, description: 'Return all vessels', type: [Vessel] })
  async findAll(): Promise<Vessel[]> {
    return this.vesselsService.findAll();
  }

  @Get(':id')
  @ApiOperation({ summary: 'Retrieve boat specifications by ID' })
  @ApiResponse({ status: 200, description: 'Return vessel by ID', type: Vessel })
  @ApiResponse({ status: 404, description: 'Vessel not found' })
  async findOne(@Param('id') id: string): Promise<Vessel> {
    return this.vesselsService.findOne(id);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update vessel specifications' })
  @ApiResponse({ status: 200, description: 'Vessel updated successfully' })
  @ApiResponse({ status: 404, description: 'Vessel not found' })
  async update(
    @Param('id') id: string,
    @Body() updateVesselDto: Partial<CreateVesselDto>,
  ): Promise<Vessel> {
    return this.vesselsService.update(id, updateVesselDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({ summary: 'Delete a vessel' })
  @ApiResponse({ status: 204, description: 'Vessel deleted successfully' })
  @ApiResponse({ status: 404, description: 'Vessel not found' })
  async remove(@Param('id') id: string): Promise<void> {
    return this.vesselsService.remove(id);
  }
}
