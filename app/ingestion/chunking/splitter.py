import re
import logfire


class ArticleChunker:
    """
    Découpe le texte brut d'un acte OHADA en chunks structurés,
    un chunk par article, avec son contexte hiérarchique.
    """

    MOTIF_ARTICLE  = re.compile(r"^\s*Article\s+\d+(\s*-\d+)*\s*$")
    MOTIF_LIVRE    = re.compile(r"^\s*Livre\s+\d+\s*-\s*(.+)$")
    MOTIF_TITRE    = re.compile(r"^\s*Titre\s+\d+\s*-\s*(.+)$")
    MOTIF_CHAPITRE = re.compile(r"^\s*Chapitre\s+.+?\s*-\s*(.+)$")
    MOTIF_SECTION  = re.compile(r"^\s*Section\s+\d+\s*-\s*(.+)$")

    def _reinitialiser(self) -> None:
        """Remet l'état de découpage à zéro (à appeler au début de chaque découpage)."""
        self.livre = self.titre = self.chapitre = self.section = None
        self.article_courant = None
        self.contenu = []
        self.articles = []

    def _fermer_article(self) -> None:
        """Scelle l'article courant avec son contexte hiérarchique et l'ajoute à la liste."""
        if self.article_courant is not None:
            texte_propre = re.sub(r"\s+", " ", " ".join(self.contenu)).strip()
            self.articles.append({
                "livre": self.livre,
                "titre": self.titre,
                "chapitre": self.chapitre,
                "section": self.section,
                "article": self.article_courant,
                "texte": texte_propre,
            })

    def _balayer(self, texte: str) -> None:
        """Parcourt le texte ligne par ligne et remplit self.articles."""
        for ligne in texte.split("\n"):
            if self.MOTIF_LIVRE.match(ligne):
                self._fermer_article()
                self.article_courant, self.contenu = None, []
                self.livre = ligne.strip()
                self.titre = self.chapitre = self.section = None

            elif self.MOTIF_TITRE.match(ligne):
                self._fermer_article()
                self.article_courant, self.contenu = None, []
                self.titre = ligne.strip()
                self.chapitre = self.section = None

            elif self.MOTIF_CHAPITRE.match(ligne):
                self._fermer_article()
                self.article_courant, self.contenu = None, []
                self.chapitre = ligne.strip()
                self.section = None

            elif self.MOTIF_SECTION.match(ligne):
                self._fermer_article()
                self.article_courant, self.contenu = None, []
                self.section = ligne.strip()

            elif self.MOTIF_ARTICLE.match(ligne):
                self._fermer_article()
                self.article_courant = ligne.strip()
                self.contenu = []

            else:
                self.contenu.append(ligne)

        self._fermer_article()  # le tout dernier article

    def _dedupliquer(self) -> None:
        """Retire les doublons consécutifs (même numéro ET même texte). Modifie self.articles."""
        resultat = []
        for chunk in self.articles:
            if (not resultat
                    or resultat[-1]["article"] != chunk["article"]
                    or resultat[-1]["texte"] != chunk["texte"]):
                resultat.append(chunk)

        nb_retires = len(self.articles) - len(resultat)
        if nb_retires:
            logfire.info(f"{nb_retires} doublon(s) retiré(s)")
        self.articles = resultat

    def _extraire_numeros(self) -> None:
        """Transforme 'Article 822-1' en '822-1' dans chaque chunk."""
        for chunk in self.articles:
            parties = chunk["article"].split(maxsplit=1)
            chunk["article"] = parties[1] if len(parties) > 1 else chunk["article"]

    def decouper(self, texte: str) -> list[dict]:
        """Point d'entrée public : texte brut -> liste de chunks structurés."""
        with logfire.span("Chunking article", taille_texte=len(texte)):
            self._reinitialiser()      # état propre à chaque appel
            self._balayer(texte)
            self._dedupliquer()
            self._extraire_numeros()

            logfire.info(f"{len(self.articles)} chunks produits")
            return self.articles