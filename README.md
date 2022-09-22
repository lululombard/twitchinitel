
# Twitchinitel

:warning: Ce projet a été fait en moins d'une heure, je m'attendais pas à avoir autant d'intéressés par [mon Tweet sur ce projet](https://twitter.com/lululombard/status/1572764632334610432), c'est vraiment du quick & dirty, j'utilise la lib pynitel n'importe comment, mais ça fonctionne.

Ce projet utilise principalement les 2 librairies suivantes :
- [Pynitel](https://github.com/cquest/pynitel)
- [twitch-chat-irc](https://github.com/xenova/twitch-chat-irc)

## Installation

```bash
git clone https://github.com/cquest/pynitel.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt -r pynitel/requirements.txt
```

## Connexion du Minitel

Il vous faut un câble série compatible avec le Minitel, personnellement j'ai un simple câble USB série FT232RL vers DIN "Peri-informatique" que j'ai fabriqué moi même. Juste une resistance de 4.7 kOhms sur TX venant du minitel, aucun composant actif contrairement à ce qui est recommandé pour le level shift, mais ça n'a pas cramé (pour l'instant).

![Câble](https://user-images.githubusercontent.com/2182934/191799004-446947ea-432c-4b20-b747-540a721e9e91.jpeg)

![Côté USB FTDI](https://user-images.githubusercontent.com/2182934/191799101-e8bc0d87-3292-40c3-9e7f-013869f1c172.jpeg)

![Côté DIN](https://user-images.githubusercontent.com/2182934/191799186-4e4314eb-ae8b-4adc-92f4-378a6a26bdcd.jpeg)

## Configuration

Si vous comptez envoyer des messages, il faut obtenir un token OAuth Twitch
1. Allez sur https://twitchapps.com/tmi/
2. Cliquez sur "Connect".
3. Connectez vous avec votre compte Twitch
4. Copiez le token auth, créez un fichier `.env` et enregistrez votre nom d'utilisateur Twitch et votre token OAuth en suivant ce format :
    > NICK=x <br> PASS=y

## Fonctionnement

Utilisation :
`python twitchinitel.py <serial_port> <channel_name>`

Exemple :
`python twitchinitel.py /dev/ttyUSB0 lululombard`

Tip : vous pouvez changer le baudrate de votre minitel à 4800 bauds en appuyant sur `Fnct + P + 4` et lancer le programme avec l'option `baudrate` pour une communication plus rapide
`python twitchinitel.py <serial_port> <channel_name> --baudrate 4800`
