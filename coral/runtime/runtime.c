#include <string.h>
#include "runtime.h"


CRValue* CRValue_new() {
    CRValue* value = (CRValue*) calloc(1, sizeof(CRValue));
    if (value == NULL) {
        CR_ABORT("FATAL: failed to allocate a new CRValue!\n");
    }
    value->_type = CR_NONE;
    value->_refCount = 1;
    value->valueDestructor = NULL;
    return value;
}

void CRValue_incref(CRValue* self) {
    CRType type = CRValue_getType(self);
    if (type == CR_INT || type == CR_BOOL) return;
    self->_refCount++;
}

void CRValue_decref(CRValue* self) {
    if (self == NULL) {
        CR_ABORT("FATAL: CRValue_decref: received NULL pointer");
        return;
    }
    CRType type = CRValue_getType(self);
    if (type == CR_INT || type == CR_BOOL) return;
    if (self->_refCount <= 0) {
        CR_ABORT("FATAL: CRValue_decref: got zero refCount!");
        return;
    }
    self->_refCount -= 1;
    if (self->_refCount <= 0) {
        if (self->valueDestructor != NULL) self->valueDestructor(self);
        free(self);
    }
}

CRType CRValue_getType(CRValue* self) {
    CR_NOT_NULL(self);
    if ((uint64_t)self & TAGGED_PTR_INT) {
        return CR_INT;
    } else if ((uint64_t)self & TAGGED_PTR_BOOL) {
        return CR_BOOL;
    } else {
        return self->_type;
    }
}

const char* CRValue_getTypeName(CRValue* self) {
    switch (CRValue_getType(self))
    {
        case CR_BOOL:
            return "bool";
        case CR_INT:
            return "int";
        case CR_CSTR:
            return "string";
        case CR_TUPLE:
            return "tuple";
        case CR_FUNCTION:
            return "function";        
        default:
            return "UNKNOWN"; 
    }
}

CRValue* CRValue_getTypeRepr(CRValue* self) {
    CRType type = CRValue_getType(self);
    if (type == CR_INT) {
        char intstr[21]; // 1 signal + 10 digits + null terminator
        int written = snprintf(intstr, sizeof(intstr), "%ld", CRValue_asInt(self));
        if (written <= 0) {
            CR_ABORT("FATAL: CRValue_getTypeRepr: snprintf failed with %d\n", written);
            return NULL;
        }
        return CRString_newCopy(intstr, written);
    } else if (type == CR_BOOL) {
        if (CRValue_asBool(self)) {
            return CRString_new("true", false);
        } else {
            return CRString_new("false", false);
        }
    } else if (type == CR_CSTR) {
        CRString* str = (CRString*)self->value;
        // " + str->value + " + null terminator
        char* repr = malloc(1 + str->length + 1 + 1);
        if (repr == NULL) {
            CR_ABORT("FATAL: CRValue_getTypeRepr: failed to allocate new buffer\n");
            return NULL;
        }
        memcpy(repr, "\"", 1);
        memcpy(repr + 1, str->value, str->length);
        memcpy(repr + (1 + str->length), "\"", 1);
        return CRString_new(repr, true);
    } else if (type == CR_TUPLE) {
        // recursive tuples will cause stack overflow
        CRTuple* tuple = self->value;
        CRValue* first = CRValue_getTypeRepr(tuple->first);
        CRValue* second = CRValue_getTypeRepr(tuple->second);
        CRString* firststr = first->value;
        CRString* secondstr = second->value;
        // "(" + firststr->value + ", " + secondstr->value + ")" + null terminator
        char* repr = malloc(1 + firststr->length + 2 + secondstr->length + 1);
        if (repr == NULL) {
            CR_ABORT("FATAL: CRValue_getTypeRepr: failed to allocate new buffer\n");
            return NULL;
        }
        size_t offset = 0;
        memcpy(repr, "(", 1);
        offset += 1;
        memcpy(repr + offset, firststr->value, firststr->length);
        offset += firststr->length;
        memcpy(repr + offset, ", ", 2);
        offset += 2;
        memcpy(repr + offset, secondstr->value, secondstr->length);
        offset += secondstr->length;
        memcpy(repr + offset, ")", 1);
        CRValue* result = CRString_new(repr, true);
        CRValue_decref(first);
        CRValue_decref(second);
        return result;
    } else {
        return CRString_new("<UNKNOWN>", false);
    }
}

void CRValue_print(CRValue* self) {
    CRValue* repr = CRValue_getTypeRepr(self);
    printf("%s\n", ((CRString*)repr->value)->value);
    CRValue_decref(repr);
}


CRValue* CRValue_newBool(bool value) {
    int64_t obj = 0;
    obj |= TAGGED_PTR_BOOL;
    obj |= (int64_t)value << TAGGED_PTR_SHIFT;
    return (CRValue*)obj;
}

bool CRValue_asBool(CRValue* self) {
    CRType type = CRValue_getType(self);
    if (type != CR_BOOL) {
        CR_ABORT("FATAL: expected bool, but got %s\n", CRValue_getTypeName(self));
        return false;
    }
    return (int64_t)self >> TAGGED_PTR_SHIFT;
}


CRValue* CRValue_newInt(int64_t value) {
    int64_t obj = 0;
    obj |= TAGGED_PTR_INT;
    obj |= value << TAGGED_PTR_SHIFT;
    return (CRValue*)obj;
}

int64_t CRValue_asInt(CRValue* self) {
    CRType type = CRValue_getType(self);
    if (type != CR_INT) {
        CR_ABORT("FATAL: expected int, but got %s\n", CRValue_getTypeName(self))
        return 0;
    }
    return (int64_t)self >> TAGGED_PTR_SHIFT;
}


CRValue* CRString_new(const char* value, bool allocated) {
    CRValue* obj = CRValue_new();
    CRString* container = (CRString*) calloc(1, sizeof(CRString));
    if (container == NULL) {
        CR_ABORT("FATAL: CRValue_newString: failed to allocate a new CRString!\n");
        return NULL;
    }
    obj->_type = CR_CSTR;
    container->value = value;
    container->length = strlen(value);
    container->allocated = allocated;
    obj->value = container;
    obj->valueDestructor = &CRString_destroyValue;
    return obj;
}

CRValue* CRString_newCopy(const char* value, size_t length) {
    CRValue* obj = CRValue_new();
    CRString* container = (CRString*) calloc(1, sizeof(CRString));
    if (container == NULL) {
        CR_ABORT("FATAL: CRString_newCopy: failed to allocate a new CRString!\n");
        return NULL;
    }
    char* copy = malloc(length + 1);
    if (copy == NULL) {
        CR_ABORT("FATAL: CRString_newCopy: failed to allocate a new CRString!\n");
        return NULL;
    }
    memcpy(copy, value, length);
    container->value = copy;
    container->length = length;
    container->allocated = true;
    obj->_type = CR_CSTR;
    obj->value = container;
    obj->valueDestructor = &CRString_destroyValue;
    return obj;
}

void CRString_destroyValue(CRValue* self) {
    CRString* str = self->value;
    if (str == NULL) return;
    if (str->allocated && str->value != NULL) {
        free((void*)(str->value));
        str->value = NULL;
    }
    free(str);
    self->value = NULL;
}

const char* CRValue_asString(CRValue* self) {
    if (CRValue_getType(self) != CR_CSTR) {
        CR_ABORT("FATAL: expected string. but got %s\n", CRValue_getTypeName(self))
        return NULL;
    }
    return ((CRString*)self->value)->value;
}


CRValue* CRValue_add(CRValue* self, CRValue* other) {
    CRType selftype = CRValue_getType(self);
    CRType othertype = CRValue_getType(other);
    if (
        selftype != CR_INT &&
        selftype != CR_CSTR &&
        othertype != CR_INT &&
        othertype != CR_CSTR
    ) {
        CR_ABORT(
            "FATAL: '+' cannot be applied between %s and %s\n",
            CRValue_getTypeName(self),
            CRValue_getTypeName(other)
        )
        return NULL;
    }
    if (selftype == CR_INT && othertype == CR_INT) {
        return CRValue_newInt(CRValue_asInt(self) + CRValue_asInt(other));
    }
    if (selftype == CR_CSTR && othertype == CR_CSTR) {
        const CRString* left = self->value;
        const CRString* right = other->value;
        char* result = malloc(left->length + right->length + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRValue_add: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, left->value, left->length);
        memcpy(result + left->length, right->value, right->length);
        return CRString_new(result, true);
    }
    if (selftype == CR_CSTR) {
        const CRString* left = self->value;
        int64_t right = CRValue_asInt(other);
        char rightstr[21];
        int written = snprintf(rightstr, sizeof(rightstr), "%ld", right);
        if (written <= 0) {
            CR_ABORT("FATAL: CRValue_getTypeRepr: snprintf failed with %d\n", written);
            return NULL;
        }
        size_t rightlen = written;
        char* result = malloc(left->length + rightlen + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRValue_add: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, left->value, left->length);
        memcpy(result + left->length, rightstr, rightlen);
        return CRString_new(result, true);
    } else {
        const CRString* right = other->value;
        int64_t left = CRValue_asInt(self);
        char leftstr[21];
        int written = snprintf(leftstr, sizeof(leftstr), "%ld", left);
        if (written <= 0) {
            CR_ABORT("FATAL: CRValue_getTypeRepr: snprintf failed with %d\n", written);
            return NULL;
        }
        size_t leftlen = written;
        char* result = malloc(leftlen + right->length + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRValue_add: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, leftstr, leftlen);
        memcpy(result + leftlen, right->value, right->length);
        return CRString_new(result, true);
    }
}

CRValue* CRValue_sub(CRValue* self, CRValue* other) {
    return CRValue_newInt(CRValue_asInt(self) - CRValue_asInt(other));
}

CRValue* CRValue_mul(CRValue* self, CRValue* other) {
    return CRValue_newInt(CRValue_asInt(self) * CRValue_asInt(other));
}

CRValue* CRValue_div(CRValue* self, CRValue* other) {
    return CRValue_newInt(CRValue_asInt(self) / CRValue_asInt(other));
}

CRValue* CRValue_mod(CRValue* self, CRValue* other) {
    return CRValue_newInt(CRValue_asInt(self) % CRValue_asInt(other));
}

CRValue* CRValue_lessThan(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asInt(self) < CRValue_asInt(other));
}

CRValue* CRValue_lessOrEqual(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asInt(self) <= CRValue_asInt(other));
}

CRValue* CRValue_greaterThan(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asInt(self) > CRValue_asInt(other));
}

CRValue* CRValue_greaterOrEqual(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asInt(self) >= CRValue_asInt(other));
}

CRValue* CRValue_and(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asBool(self) && CRValue_asBool(other));
}

CRValue* CRValue_or(CRValue* self, CRValue* other) {
    return CRValue_newBool(CRValue_asBool(self) || CRValue_asBool(other));
}


CRValue* CRValue_equals(CRValue* self, CRValue* other) {
    CRType selftype = CRValue_getType(self);
    CRType othertype = CRValue_getType(other);
    if (selftype == CR_INT && othertype == CR_INT) {
        return CRValue_newBool(CRValue_asInt(self) == CRValue_asInt(other));
    }
    if (selftype == CR_BOOL && othertype == CR_BOOL) {
        return CRValue_newBool(CRValue_asBool(self) == CRValue_asBool(other));
    }
    if (selftype == CR_CSTR && othertype == CR_CSTR) {
        if (((CRString*)self->value)->length != ((CRString*)other->value)->length) {
            return CRValue_newBool(false);
        }
        return CRValue_newBool(strcmp(
            ((CRString*)self->value)->value,
            ((CRString*)other->value)->value
        ));
    }
    CR_ABORT("FATAL: equality cannot be applied between %s and %s\n", CRValue_getTypeName(self), CRValue_getTypeName(other))
    return NULL;
}

CRValue* CRValue_notEquals(CRValue* self, CRValue* other) {
    return CRValue_newBool(!CRValue_asBool(CRValue_equals(self, other)));
}


CRValue* CRTuple_new(CRValue* first, CRValue* second) {
    CRValue* obj = CRValue_new();
    CRTuple* tuple = (CRTuple*) calloc(1, sizeof(CRTuple));
    if (tuple == NULL) {
        CR_ABORT("FATAL: CRTuple_new: failed to allocate a new CRTuple!\n");
        return NULL;
    }
    tuple->first = first;
    tuple->second = second;
    obj->_type = CR_TUPLE;
    obj->value = tuple;
    obj->valueDestructor = &CRTuple_destroyValue;
    CRValue_incref(first);
    CRValue_incref(second);
    return obj;
}

void CRTuple_destroyValue(CRValue* self) {
    if (self->value == NULL) return;
    CRTuple* tuple = (CRTuple*) self->value;
    CRValue_decref(tuple->first);
    CRValue_decref(tuple->second);
    free(tuple);
    self->value = NULL;
}

const CRTuple* CRValue_asTuple(CRValue* self) {
    if (CRValue_getType(self) != CR_TUPLE) {
        CR_ABORT("FATAL: expected tuple, but got %s\n", CRValue_getTypeName(self));
        return NULL;
    }
    return self->value;
}

CRValue* CRTuple_getFirst(CRValue* self) {
    return CRValue_asTuple(self)->first;
}

CRValue* CRTuple_getSecond(CRValue* self) {
    return CRValue_asTuple(self)->second;
}
