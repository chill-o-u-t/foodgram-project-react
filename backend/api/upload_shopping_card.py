@property
def create_cart(ingredients, author):
    shopping_list = (f'Список покупок :{author}')
    for ing in ingredients:
        shopping_list += (
            f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
        )
    return shopping_list


