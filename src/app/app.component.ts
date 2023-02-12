import { Component, OnInit } from '@angular/core';
import { AngularFireDatabase } from '@angular/fire/compat/database';
import { list } from 'rxfire/database';
import { Etudiant, Place } from './models';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'attendanceTracker';

  daysArray = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
  date = new Date();
  day = this.daysArray[this.date.getDay()];
  
  tablePresences: any[] = [];
  displayedColumns: string[] = ["idEtudiant", "nomEtudiant", "prenomEtudiant", "niveauEtudiant", "groupeEtudiant", "idPlace", "estOccupee"];
  etudiants: Etudiant[] = [];
  places: Place[] = [];

  constructor(private db: AngularFireDatabase) {

  }

  ngOnInit() {
    setInterval(() => {
      this.date = new Date();
      this.day = this.daysArray[this.date.getDay()];
      
    }, 1000);

    this.db.list('etudiants')
      .valueChanges()
        .subscribe((liste_etudiants: any[]) => this.etudiants = liste_etudiants);
    this.db.list('places')
      .valueChanges()
        .subscribe((liste_places: any[]) => {
            this.places = liste_places;
            const mergeById = (etudiants: Etudiant[], places: Place[]) =>
              etudiants.map(etudiant => ({
                  ...places.find((place) => (place.idPlace === etudiant.idEtudiant) && place),
                  ...etudiant
            }));
  
            this.tablePresences = mergeById(this.etudiants, this.places);
        });  
  }
}
