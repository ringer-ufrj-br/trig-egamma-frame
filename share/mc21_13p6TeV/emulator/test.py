  
def test():
  # rings presmaple 
  presample = [iring for iring in range(8//2)]
  # EM1 list
  sum_rings = 8
  em1 = [iring for iring in range(sum_rings, sum_rings+(64//2))]
  # EM2 list
  sum_rings = 8+64
  em2 = [iring for iring in range(sum_rings, sum_rings+(8//2))]

  # EM3 list
  sum_rings = 8+64+8
  em3 = [iring for iring in range(sum_rings, sum_rings+(8//2))]

  # HAD1 list
  sum_rings = 8+64+8+8
  had1 = [iring for iring in range(sum_rings, sum_rings+(4//2))]

  # HAD2 list
  sum_rings = 8+64+8+8+4
  had2 = [iring for iring in range(sum_rings, sum_rings+(4//2))]

  # HAD3 list
  sum_rings = 8+64+8+8+4+4
  had3 = [iring for iring in range(sum_rings, sum_rings+(4//2))]

  col_names = presample+em1+em2+em3+had1+had2+had3
  
  print(col_names)

test()
