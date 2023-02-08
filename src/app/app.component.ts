import { Component, OnInit } from '@angular/core';
import { AngularFireDatabase } from '@angular/fire/compat/database';
import { Etudiant } from './model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  
  title = 'attendanceTracker';
  daysArray = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
  date = new Date();
  displayedColumns: string[] = ["idEtudiant", "nomEtudiant", "prenomEtudiant", "place", "placeOccupee", "heure"];
  dataSource: Etudiant[] = [
    { idEtudiant: 1, nomEtudiant: 'Nom', prenomEtudiant: 'Aymane', place: 10, placeOccupee: true, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Nom2', prenomEtudiant: 'Aymane', place: 10, placeOccupee: false, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Nom3', prenomEtudiant: 'hamza', place: 10, placeOccupee: true, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Nom', prenomEtudiant: 'Aymane', place: 10, placeOccupee: true, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Nom4', prenomEtudiant: 'kawtar', place: 10, placeOccupee: true, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Nom', prenomEtudiant: 'Aymane', place: 10, placeOccupee: false, heure: '10:10:20' },
    { idEtudiant: 1, nomEtudiant: 'Chaki', prenomEtudiant: 'Aymane', place: 10, placeOccupee: false, heure: '10:10:20' },
  ];


  constructor(db: AngularFireDatabase) {

  }

  ngOnInit() {
    console.log(this.dataSource);
  }

}
