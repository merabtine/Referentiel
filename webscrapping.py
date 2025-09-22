import json
import nodriver as uc
import asyncio
import pandas as pd

async def main():
    print("🌍 Lancement du navigateur...")
    browser = await uc.start()
    page = await browser.get("https://www.oscaro.com")

    # Injection du localStorage
    try:
        with open("auth.json", "r", encoding="utf-8") as f:
            auth_data = json.load(f)
        for origin_data in auth_data.get("origins", []):
            local_storage = origin_data.get("localStorage", [])
            local_storage_dict = {item["name"]: item["value"] for item in local_storage}
            await page.set_local_storage(local_storage_dict)
        print("✅ Cookies et localStorage injectés")
    except FileNotFoundError:
        print("❌ auth.json non trouvé")

    await asyncio.sleep(30)  # Attendre le chargement complet

    # Récupération des catégories principales
    containers = await page.query_selector_all("div.category-item-header h2 a")
    print(f"Nombre de catégories trouvées : {len(containers)}")

    all_data = []

    # Parcours des catégories principales
    for i, el in enumerate(containers):
        try:
            cat_nom = el.text.strip()
            cat_href = el.attrs.get('href', '').strip()
            if cat_href and not cat_href.startswith("http"):
                cat_href = "https://www.oscaro.com" + cat_href
            print(f"\n{i+1}️⃣ Catégorie : {cat_nom} -> {cat_href}")

            # Charger la page de la catégorie
            cat_page = await browser.get(cat_href)
            await asyncio.sleep(5)

            # Récupérer les sous-catégories
            subcontainers = await cat_page.query_selector_all("div.category-item-header h2 a")
            print(f"   ↪ Sous-catégories trouvées : {len(subcontainers)}")

            for j, sub in enumerate(subcontainers):
                try:
                    sub_nom = sub.text.strip()
                    sub_href = sub.attrs.get('href', '').strip()
                    if sub_href and not sub_href.startswith("http"):
                        sub_href = "https://www.oscaro.com" + sub_href
                    print(f"   {j+1}. {sub_nom} -> {sub_href}")

                    # Aller sur la page de la sous-catégorie
                    sub_page = await browser.get(sub_href)
                    await asyncio.sleep(5)

                    # Récupérer les produits de la sous-catégorie
                    subsubcontainers = await sub_page.query_selector_all(
                        "div.link-list-column ul.link-list.link-primary li a"
                    )

                    produits = []
                    for k, s in enumerate(subsubcontainers):
                        try:
                            s_nom = s.text.strip()
                            s_href = s.attrs.get('href', '').strip() if s.attrs.get('href') else ""
                            if s_href and not s_href.startswith("http"):
                                s_href = "https://www.oscaro.com" + s_href
                            produits.append(s_nom)
                            print(f"       → Produit {k+1}: {s_nom}")
                        except:
                            print("aucun produit trouvé")

                    if not produits:
                        produits = ["Aucun produit trouvé"]

                    all_data.append({
                        "Catégorie": cat_nom,
                        "Sous-catégorie": sub_nom,
                        "Lien": sub_href,
                        "Produits": ", ".join(produits)
                    })

                except Exception as e_sub:
                    print(f"❌ Erreur sous-catégorie {j+1} de {cat_nom} :", e_sub)

        except Exception as e_cat:
            print(f"❌ Erreur catégorie {i+1} :", e_cat)

    # Sauvegarder dans un CSV
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("Organe_SousOrgane_Produits_oscaro.csv", index=False, encoding="utf-8-sig")
        print("✅ CSV généré avec succès")
    else:
        print("❌ Aucun élément trouvé")

    # Fermer le navigateur
    if browser:
        browser.stop()
        print("🚀 Navigateur fermé.")

if __name__ == "__main__":
    asyncio.run(main())
