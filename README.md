# Comment installer Poppler
Poppler est une bibliothèque open source pour le rendu de fichiers PDF. Il est utilisé par notre lecteur PDF pour afficher les fichiers PDF. Voici comment l'installer sur différents systèmes d'exploitation :

# Sous Windows
Téléchargez le fichier d'installation de Poppler à partir de la page de téléchargement officielle : https://blog.alivate.com.au/poppler-windows/
Exécutez le fichier d'installation et suivez les instructions à l'écran pour installer Poppler.

Ajoutez le chemin d'installation de Poppler à la variable d'environnement PATH de votre système pour que le lecteur PDF puisse le trouver. Pour cela, cliquez avec le bouton droit sur "Ce PC" -> "Propriétés" -> "Paramètres système avancés" -> "Variables d'environnement" -> dans la section "Variables système", cherchez la variable PATH -> cliquez sur "Modifier" -> ajoutez le chemin d'installation de Poppler (par exemple, C:\Program Files (x86)\Poppler\bin) à la fin de la ligne -> cliquez sur "OK" pour enregistrer les modifications.
# Sous Linux
Ouvrez le terminal et exécutez la commande suivante pour installer Poppler :

sudo apt-get install poppler-utils

Si vous utilisez une distribution Linux différente, utilisez le gestionnaire de paquets approprié pour installer Poppler.
Si vous rencontrez des problèmes pour afficher des fichiers PDF avec notre lecteur PDF, vérifiez que la bibliothèque Poppler est bien installée et que le chemin d'installation est correctement configuré.
# Sous macOS
Installez Homebrew, le gestionnaire de paquets pour macOS, en suivant les instructions sur la page officielle : https://brew.sh/index_fr
Ouvrez le terminal et exécutez la commande suivante pour installer Poppler :

brew install poppler

Si vous rencontrez des problèmes pour afficher des fichiers PDF avec notre lecteur PDF, vérifiez que la bibliothèque Poppler est bien installée et que le chemin d'installation est correctement configuré.
Nous espérons que ces instructions vous aideront à installer Poppler avec succès sur votre système d'exploitation et à utiliser notre lecteur PDF sans problème. Si vous rencontrez des problèmes lors de l'installation ou de l'utilisation, n'hésitez pas à nous contacter pour obtenir de l'aide.




