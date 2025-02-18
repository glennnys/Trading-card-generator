CREATE VIEW get_card_types AS
SELECT t.type, t.passive, ct.isPrimary, t.colorR, t.colorG, t.colorB, c.name as name FROM cardsXtypes ct
INNER JOIN cards c ON c.cardID = ct.cardID
INNER JOIN types t ON t.typeID = ct.typeID;

CREATE VIEW get_cards AS
SELECT name, vt.variant, cardID 
FROM Cards c 
INNER JOIN CardVariants vt 
ON c.variantType = vt.variantID

CREATE VIEW get_cards_infos AS
SELECT c.name, c.description, c.hp, pre.name as prevolve, c.retreat, r.rarity, c.illustrator, c.entry, c.image, 
c.upperleftx as crop1, c.upperlefty as crop2, c.bottomrightx as crop3, c.bottomrighty as crop4 FROM cards c
INNER JOIN rarities r ON c.rarity = r.rarityID
LEFT JOIN Cards pre ON pre.cardID = c.prevolve;

CREATE VIEW get_move_costs AS
SELECT t.type as type, mc.amount as amount, mc.volatile as volatile, m.moveName as name FROM moveCosts mc
RIGHT JOIN moves m ON m.moveID = mc.moveID
INNER JOIN types t ON t.typeID = mc.typeID;

CREATE VIEW get_moves AS
select m.moveName, t.type, m.damage, m.description, m.isAbility, t.colorR as R, t.colorG as G, t.colorB as B, c.name as name from cardsXMoves cm
INNER JOIN Cards c ON c.cardID = cm.cardID
INNER JOIN Moves m ON m.moveID = cm.moveID
LEFT JOIN types t ON t.typeID = m.typeID;