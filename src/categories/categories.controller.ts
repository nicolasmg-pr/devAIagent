import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  UseGuards,
  Request,
} from '@nestjs/common';
import { CategoriesService } from './categories.service';
import { CreateCategoryDto } from './dto/create-category.dto';
import { UpdateCategoryDto } from './dto/update-category.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('api/v1/categories')
@UseGuards(JwtAuthGuard)
export class CategoriesController {
  constructor(private categoriesService: CategoriesService) {}

  @Get()
  async findAll(@Request() req) {
    return this.categoriesService.findAll(req.user.userId);
  }

  @Get(':id')
  async findOne(@Param('id') id: string, @Request() req) {
    return this.categoriesService.findOne(id, req.user.userId);
  }

  @Post()
  async create(@Body() createCategoryDto: CreateCategoryDto, @Request() req) {
    const category = await this.categoriesService.create(createCategoryDto, req.user.userId);
    return {
      id: category.id,
      message: 'Categoría creada exitosamente',
    };
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateCategoryDto: UpdateCategoryDto,
    @Request() req,
  ) {
    await this.categoriesService.update(id, updateCategoryDto, req.user.userId);
    return {
      id,
      message: 'Categoría actualizada exitosamente',
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @Request() req) {
    await this.categoriesService.remove(id, req.user.userId);
    return {
      id,
      message: 'Categoría eliminada exitosamente',
    };
  }
}
