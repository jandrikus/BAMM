// entradas de los pulsadores
const int botonRojo = 13;
const int botonBlanco = 6;
const int botonReset = 7;
const int botonNext = 10;
const int botonPlata = 2;
const int botonAzul = 4;
const int botonAmarillo = 5;

const int electroiman_PWM = 11;

// contadores de cuantas veces se ha pulsado tal pulsador
int rojoCounter = 0;
int blancoCounter = 0;
int nextCounter = 0;

char respuesta50[3];
char respuesta51[10];

char rojo[2];
char blanco[2];
char amar[2];
char plata[2];
char azul[2];

bool a;

void setup() {
  pinMode(botonRojo,INPUT);
  pinMode(botonAmarillo,INPUT);
  pinMode(botonAzul,INPUT);
  pinMode(botonPlata,INPUT);
  pinMode(botonBlanco,INPUT);
  pinMode(botonNext,INPUT);
  pinMode(botonReset,INPUT);
  // comenzamos una comunicacion con el arduino
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    byte resp = Serial.read();
    if(resp==49){
      analogWrite(electroiman_PWM,255);
    }
    else if (resp==48) {
      analogWrite(electroiman_PWM,0);
    }
    else if (resp==50) {
      a = true;
      rojoCounter = 0;
      blancoCounter = 0;
      while(a) {
        //interaccion 4 pulsadores
        if (digitalRead(botonRojo) == LOW) {
          rojoCounter += 1;
          delay(300);
        }
        else if (digitalRead(botonBlanco) == LOW) {
          blancoCounter += 1;
          delay(300);
        }
        else if (digitalRead(botonNext) == LOW) {
          a = false;
          sprintf(respuesta50, "%d|%d\n", rojoCounter, blancoCounter);
          Serial.write(respuesta50);
          delay(300);
        }
        else if (digitalRead(botonReset) == LOW) {
          rojoCounter = 0;
          blancoCounter = 0;
          delay(300);
        }
      }
    }
    else if (resp==51) {
      a = true;
      sprintf(rojo,'\0');
      sprintf(blanco,'\0');
      sprintf(amar,'\0');
      sprintf(azul,'\0');
      sprintf(plata,'\0');
      sprintf(respuesta51, '\0');
      while(a) {
        //interaccion 7 pulsadores
        if (digitalRead(botonReset) == LOW) {
          sprintf(rojo,'\0');
          sprintf(blanco,'\0');
          sprintf(amar,'\0');
          sprintf(azul,'\0');
          sprintf(plata,'\0');
          sprintf(respuesta51, '\0');
          delay(300);
        }
        else if (digitalRead(botonRojo) == LOW) {
          sprintf(rojo, "%d|",4);
          strcat(respuesta51,rojo);
          delay(300);
        }
        else if (digitalRead(botonBlanco) == LOW) {
          sprintf(blanco, "%d|",3);
          strcat(respuesta51,blanco);
          delay(300);
        }
        else if (digitalRead(botonAmarillo) == LOW) {
          sprintf(amar, "%d|",2);
          strcat(respuesta51,amar);
          delay(300);
        }
        else if (digitalRead(botonPlata) == LOW) {
          sprintf(plata, "%d|",0);
          strcat(respuesta51,plata);
          delay(300);
        }
        else if (digitalRead(botonAzul) == LOW) {
          sprintf(azul, "%d|",1);
          strcat(respuesta51,azul);
          delay(300);
        }
        else if (digitalRead(botonNext) == LOW) {
          a = false;
          Serial.write(respuesta51);
          delay(300);
        }
        
      }
    }
  }
}
