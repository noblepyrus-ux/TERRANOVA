import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Fincas } from './fincas';

describe('Fincas', () => {
  let component: Fincas;
  let fixture: ComponentFixture<Fincas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Fincas],
    }).compileComponents();

    fixture = TestBed.createComponent(Fincas);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
