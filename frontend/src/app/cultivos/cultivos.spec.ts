import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Cultivos } from './cultivos';

describe('Cultivos', () => {
  let component: Cultivos;
  let fixture: ComponentFixture<Cultivos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Cultivos],
    }).compileComponents();

    fixture = TestBed.createComponent(Cultivos);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
