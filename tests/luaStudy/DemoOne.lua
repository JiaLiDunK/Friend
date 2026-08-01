---
--- Created by 33717
--- DateTime: 2026/6/20 10:57
---

print("Hello World")
i = 1
print(type(i))

do
    local xx = 2
    print(i,xx)
end
print(xx)

arr = {1,2,3,4,"happy",true}
print(arr[1],#arr)
print(type(arr))
for i = 1, #arr do
    print(arr[i])
end
for i,v in ipairs(arr) do
    print(i,v)
end