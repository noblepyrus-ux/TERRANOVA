import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'formatoPesos',
  standalone: true
})
export class FormatoPesosPipe implements PipeTransform {
  transform(value: number | string | null | undefined): string {
    if (value === null || value === undefined || value === '') return '$ 0';
    
    // Convertir a número
    const num = typeof value === 'string' 
      ? parseFloat(value.replace(/\./g, '').replace(',', '.')) 
      : value;
      
    if (isNaN(num)) return '$ 0';

    // Formatear manualmente para garantizar el formato colombiano
    // Separador de miles: punto (.)
    // Separador decimal: coma (,)
    
    const partes = num.toFixed(2).split('.');
    const entero = partes[0];
    const decimal = partes[1];
    
    // Agregar puntos de miles
    const enteroFormateado = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `$ ${enteroFormateado},${decimal}`;
  }
}