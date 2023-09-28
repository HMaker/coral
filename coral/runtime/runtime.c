#include "runtime.h"


CRObject* CRObject_new() {
    CRObject* value = (CRObject*) calloc(1, sizeof(CRObject));
    if (value == NULL) {
        CR_ABORT("FATAL: failed to allocate a new CRObject!\n");
        return NULL;
    }
    value->_type = CR_UNDEFINED;
    value->_refCount = 1;
    return value;
}


void CRObject_decref(CRObject* self) {
    if (self == NULL) {
        CR_ABORT("FATAL: CRObject_decref: received NULL pointer");
        return;
    }
    CRType type = CRObject_getType(self);
    if (type == CR_INT || type == CR_BOOL) return;
    if (self->_refCount <= 0) {
        CR_ABORT("FATAL: CRObject_decref: got zero refCount!");
        return;
    }
    self->_refCount -= 1;
    if (self->_refCount <= 0) {
        switch (type) {
            case CR_STR:
                CRString_destroy(self->value);
                break;
            case CR_TUPLE:
                CRTuple_destroy(self->value);
                break;
            case CR_FUNCTION:
                CRFunction_destroy(self->value);
                break;
            default:
                CR_ABORT("FATAL: CRObject_decref: unknown CRObject type!");
                return;
        }
        free(self);
    }
}


const char* CRObject_getTypeName(CRObject* self) {
    switch (CRObject_getType(self))
    {
        case CR_BOOL:
            return "bool";
        case CR_INT:
            return "int";
        case CR_STR:
            return "string";
        case CR_TUPLE:
            return "tuple";
        case CR_FUNCTION:
            return "function";        
        default:
            return "unknown"; 
    }
}


CRObject* CRObject_getTypeRepr(CRObject* self) {
    CRType type = CRObject_getType(self);
    if (type == CR_INT) {
        char intstr[21]; // 1 signal + 10 digits + null terminator
        int written = snprintf(intstr, sizeof(intstr), "%ld", CRObject_asInt(self));
        if (written <= 0) {
            CR_ABORT("FATAL: CRObject_getTypeRepr: snprintf failed with %d\n", written);
            return NULL;
        }
        return CRString_newCopy(intstr, written);
    } else if (type == CR_BOOL) {
        if (CRObject_asBool(self)) {
            return CRString_new("true", false);
        } else {
            return CRString_new("false", false);
        }
    } else if (type == CR_STR) {
        return CRString_repr(self->value);
    } else if (type == CR_TUPLE) {
        return CRTuple_repr(self->value);
    } else if (type == CR_FUNCTION) {
        return CRString_new("<#closure>", false);
    } else {
        return CRString_new("unknown", false);
    }
}


void CRObject_print(CRObject* self) {
    CRObject* repr = CRObject_getTypeRepr(self);
    printf("%s\n", ((CRString*)repr->value)->value);
    CRObject_decref(repr);
}


CRObject* CRObject_add(CRObject* self, CRObject* other) {
    CRType selftype = CRObject_getType(self);
    CRType othertype = CRObject_getType(other);
    if (
        selftype != CR_INT &&
        selftype != CR_STR &&
        othertype != CR_INT &&
        othertype != CR_STR
    ) {
        CR_ABORT(
            "FATAL: '+' cannot be applied between %s and %s\n",
            CRObject_getTypeName(self),
            CRObject_getTypeName(other)
        )
        return NULL;
    }
    if (selftype == CR_INT && othertype == CR_INT) {
        return CRObject_newInt(CRObject_asInt(self) + CRObject_asInt(other));
    }
    return CRString_concat(self, other);
}


CRObject* CRObject_equals(CRObject* self, CRObject* other) {
    CRType selftype = CRObject_getType(self);
    CRType othertype = CRObject_getType(other);
    if (selftype == CR_INT && othertype == CR_INT) {
        return CRObject_newBool(CRObject_asInt(self) == CRObject_asInt(other));
    }
    if (selftype == CR_BOOL && othertype == CR_BOOL) {
        return CRObject_newBool(CRObject_asBool(self) == CRObject_asBool(other));
    }
    if (selftype == CR_STR && othertype == CR_STR) {
        return CRString_equals((CRString*)self->value, (CRString*)other->value);
    }
    CR_ABORT("FATAL: equality cannot be applied between %s and %s\n", CRObject_getTypeName(self), CRObject_getTypeName(other))
    return NULL;
}
