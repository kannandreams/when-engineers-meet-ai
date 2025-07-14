import numpy as np
from decimal import Decimal
# Original high-precision decimal input
original = Decimal('3.1415')

# Convert to float32 (NumPy) and then to Python float
float32_val_np = np.float32(original)
float32_val = float(float32_val_np)  # convert to Python float
stored_as_decimal = Decimal(repr(float32_val))  # get full precision

# Int8 conversion
int8_val_np = np.int8(round(original))
int8_val = int(int8_val_np)
stored_as_int8_decimal = Decimal(int8_val)

# Print results
print("Original Decimal         :", original)
print()
print("Float32 stored value     :", stored_as_decimal)
print("Float32 raw float        :", repr(float32_val))
print("Loss due to float32      :", original - stored_as_decimal)
print("Memory used (float32)    :", float32_val_np.nbytes, "bytes")
print()
print("Int8 stored value        :", int8_val)
print("Int8 as Decimal          :", stored_as_int8_decimal)
print("Loss due to int8         :", original - stored_as_int8_decimal)
print("Memory used (int8)       :", int8_val_np.nbytes, "bytes")
