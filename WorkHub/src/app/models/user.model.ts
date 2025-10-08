export interface User { //MODELLO PER USER GENERALE
    anni_di_esperienza: number;
    country: string;
    
    // 2. Dati di Contatto e Base
    email: string;
    eta: number;
    first_name: string;
    gender: 'M' | 'F' | string; 
    last_name: string;

    // 3. Dati Tecnici e Stato
    skills: string | null; // Stringa di skill concatenate (es: "HTML,CSS,JavaScript")
    status: 'libero' | 'occupato' | string;
    
    // 4. Identificativi
    user_id: number;
    username: string;
}