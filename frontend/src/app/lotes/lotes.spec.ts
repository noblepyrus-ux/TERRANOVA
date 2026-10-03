import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Lotes } from './lotes';

describe('Lotes', () => {
  let component: Lotes;
  let fixture: ComponentFixture<Lotes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Lotes],
    }).compileComponents();

    fixture = TestBed.createComponent(Lotes);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
