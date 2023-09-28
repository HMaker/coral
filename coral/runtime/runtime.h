#ifndef CR_RUNTIME_H
#define CR_RUNTIME_H

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>


#define CR_ABORT(...) fprintf(stderr, __VA_ARGS__); \
                      fflush(stderr); \
                      exit(EXIT_FAILURE);
#define CR_NOT_NULL(obj) if ((obj) == NULL) {  CR_ABORT("FATAL: received NULL object!\n");  }


#define TAGGED_PTR_INT   1
#define TAGGED_PTR_BOOL  2
#define TAGGED_PTR_SHIFT 2


typedef enum
{
    CR_UNDEFINED,
    CR_BOOL,
    CR_INT,
    CR_STR,
    CR_TUPLE,
    CR_FUNCTION
} CRType;


typedef struct {
  CRType _type;
  unsigned long _refCount;
  void* value;
} CRObject;


typedef struct {
    const char* value;
    size_t length;
    bool owner;
} CRString;


typedef struct {
    CRObject* first;
    CRObject* second;
} CRTuple;


typedef struct {
    CRObject** objects;
    size_t length;
    size_t maxLength;
} CRObjectArray;


typedef struct {
    unsigned short arity;
    CRObjectArray* globals;
    CRObject* (*fp) (CRObject**, CRObject**);
} CRFunction;


CRObject* CRObject_new(void);
inline CRType CRObject_getType(CRObject* self) {
    CR_NOT_NULL(self);
    if ((uint64_t)self & TAGGED_PTR_INT) {
        return CR_INT;
    } else if ((uint64_t)self & TAGGED_PTR_BOOL) {
        return CR_BOOL;
    } else {
        return self->_type;
    }
}
inline void CRObject_incref(CRObject* self) {
    CRType type = CRObject_getType(self);
    if (type == CR_INT || type == CR_BOOL) return;
    self->_refCount++;
}
void CRObject_decref(CRObject* self);

const char* CRObject_getTypeName(CRObject* self);
CRObject* CRObject_getTypeRepr(CRObject* self);
void CRObject_print(CRObject* self);


/**********************************************************************************************
 * INTEGER
**********************************************************************************************/

inline CRObject* CRObject_newInt(int64_t value) {
    int64_t obj = 0;
    obj |= TAGGED_PTR_INT;
    obj |= value << TAGGED_PTR_SHIFT;
    return (CRObject*)obj;
}
inline int64_t CRObject_asInt(CRObject* self) {
    CRType type = CRObject_getType(self);
    if (type != CR_INT) {
        CR_ABORT("FATAL: expected int, but got %s\n", CRObject_getTypeName(self))
        return 0;
    }
    return (int64_t)self >> TAGGED_PTR_SHIFT;
}
CRObject* CRObject_add(CRObject* self, CRObject* other);
inline CRObject* CRObject_sub(CRObject* self, CRObject* other) {
    return CRObject_newInt(CRObject_asInt(self) - CRObject_asInt(other));
}
inline CRObject* CRObject_mul(CRObject* self, CRObject* other) {
    return CRObject_newInt(CRObject_asInt(self) * CRObject_asInt(other));
}
inline CRObject* CRObject_div(CRObject* self, CRObject* other) {
    return CRObject_newInt(CRObject_asInt(self) / CRObject_asInt(other));
}
inline CRObject* CRObject_mod(CRObject* self, CRObject* other) {
    return CRObject_newInt(CRObject_asInt(self) % CRObject_asInt(other));
}


/**********************************************************************************************
 * BOOLEAN
**********************************************************************************************/

inline CRObject* CRObject_newBool(bool value) {
    int64_t obj = 0;
    obj |= TAGGED_PTR_BOOL;
    obj |= (int64_t)value << TAGGED_PTR_SHIFT;
    return (CRObject*)obj;
}
inline bool CRObject_asBool(CRObject* self) {
    CRType type = CRObject_getType(self);
    if (type != CR_BOOL) {
        CR_ABORT("FATAL: expected bool, but got %s\n", CRObject_getTypeName(self));
        return false;
    }
    return (int64_t)self >> TAGGED_PTR_SHIFT;
}
inline CRObject* CRObject_lessThan(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asInt(self) < CRObject_asInt(other));
}
inline CRObject* CRObject_lessOrEqual(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asInt(self) <= CRObject_asInt(other));
}
inline CRObject* CRObject_greaterThan(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asInt(self) > CRObject_asInt(other));
}
inline CRObject* CRObject_greaterOrEqual(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asInt(self) >= CRObject_asInt(other));
}
inline CRObject* CRObject_and(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asBool(self) && CRObject_asBool(other));
}
inline CRObject* CRObject_or(CRObject* self, CRObject* other) {
    return CRObject_newBool(CRObject_asBool(self) || CRObject_asBool(other));
}
CRObject* CRObject_equals(CRObject* self, CRObject* other);
inline CRObject* CRObject_notEquals(CRObject* self, CRObject* other) {
    return CRObject_newBool(!CRObject_asBool(CRObject_equals(self, other)));
}


/**********************************************************************************************
 * STRING
**********************************************************************************************/

CRObject* CRString_new(const char* value, bool owner);
CRObject* CRString_newCopy(const char* value, size_t length);
void CRString_destroy(CRString* self);
CRObject* CRString_concat(CRObject* self, CRObject* other);
CRObject* CRString_equals(CRString* self, CRString* other);
inline const char* CRObject_asString(CRObject* self) {
    if (CRObject_getType(self) != CR_STR) {
        CR_ABORT("FATAL: expected string. but got %s\n", CRObject_getTypeName(self))
        return NULL;
    }
    return ((CRString*)self->value)->value;
}
CRObject* CRString_repr(CRString* self);


/**********************************************************************************************
 * TUPLE
**********************************************************************************************/

CRObject* CRTuple_new(CRObject* first, CRObject* second);
void CRTuple_destroy(CRTuple* self);
inline const CRTuple* CRObject_asTuple(CRObject* self) {
    if (CRObject_getType(self) != CR_TUPLE) {
        CR_ABORT("FATAL: expected tuple, but got %s\n", CRObject_getTypeName(self));
        return NULL;
    }
    return self->value;
}
CRObject* CRTuple_getFirst(CRObject* self);
CRObject* CRTuple_getSecond(CRObject* self);
CRObject* CRTuple_repr(CRTuple* self);


/**********************************************************************************************
 * FUNCTION
**********************************************************************************************/

CRObjectArray* CRObjectArray_new(size_t maxLength);
void CRObjectArray_release(CRObjectArray* self);
void CRObjectArray_destroy(CRObjectArray* self);
void CRObjectArray_push(CRObjectArray* self, CRObject* object);
void CRObjectArray_insert(CRObjectArray* self, size_t index, CRObject* object);
CRObject* CRObjectArray_get(CRObjectArray* self, size_t index);

CRObject* CRFunction_new(
    size_t globalsSize,
    unsigned short arity,
    CRObject* (*fp) (CRObject**, CRObject**)
);
void CRFunction_destroy(CRFunction* self);
void CRFunction_setGlobal(CRObject* self, size_t index, CRObject* global);
CRObject* CRFunction_call(CRObject* self, size_t argscount, ...);

#endif