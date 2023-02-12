export interface Etudiant {
  idEtudiant: number;
  nomEtudiant: string;
  prenomEtudiant: string;
  niveauEtudiant: string;
  groupeEtudiant: string;
}

export interface Place {
  idPlace: number;
  idEtudiant: number;
  estOccupee: boolean;
}