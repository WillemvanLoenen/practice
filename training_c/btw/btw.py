def btw():
    kostprijs_excl = float(input("Geef de kostprijs van het product, exclusief btw: "))
    verkoopprijs_incl = float(input("Geef de gewenste verkoopprijs van het product, inclusief btw: "))
    btw_hoog = 21
    betaalde_btw = kostprijs_excl * btw_hoog / 100
    ontvangen_btw = verkoopprijs_incl * btw_hoog / (100 + btw_hoog)
    verschuldigde_btw = ontvangen_btw - betaalde_btw
    print(f"De verschuldigde btw is {verschuldigde_btw}")


if __name__ == "__main__":
    btw()
