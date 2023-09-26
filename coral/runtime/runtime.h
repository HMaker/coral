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
    CR_NONE,
    CR_BOOL,
    CR_INT,
    CR_CSTR,
    CR_TUPLE,
    CR_FUNCTION
} CRType;

typedef struct CRValue {
  CRType _type;
  unsigned long _refCount;
  void* value;
  void (*valueDestructor) (struct CRValue*);
} CRValue;

typedef struct {
    const char* value;
    size_t length;
    bool allocated;
} CRString;

typedef struct {
    CRValue* first;
    CRValue* second;
} CRTuple;

typedef struct {
    uint16_t arity;
    CRValue* nonlocals;
} CRFunction;


static inline CRValue* CRValue_new(void);
inline void CRValue_incref(CRValue* self);
void CRValue_decref(CRValue* self);

static inline CRType CRValue_getType(CRValue* self);
static const char* CRValue_getTypeName(CRValue* self);
static CRValue* CRValue_getTypeRepr(CRValue* self);
void CRValue_print(CRValue* self);

static inline CRValue* CRValue_newInt(int64_t value);
static inline int64_t CRValue_asInt(CRValue* self);
CRValue* CRValue_add(CRValue* self, CRValue* other);
inline CRValue* CRValue_sub(CRValue* self, CRValue* other);
inline CRValue* CRValue_mul(CRValue* self, CRValue* other);
inline CRValue* CRValue_div(CRValue* self, CRValue* other);
inline CRValue* CRValue_mod(CRValue* self, CRValue* other);

static inline CRValue* CRValue_newBool(bool value);
static inline bool CRValue_asBool(CRValue* self);
inline CRValue* CRValue_lessThan(CRValue* self, CRValue* other);
inline CRValue* CRValue_lessOrEqual(CRValue* self, CRValue* other);
inline CRValue* CRValue_greaterThan(CRValue* self, CRValue* other);
inline CRValue* CRValue_greaterOrEqual(CRValue* self, CRValue* other);
inline CRValue* CRValue_and(CRValue* self, CRValue* other);
inline CRValue* CRValue_or(CRValue* self, CRValue* other);
CRValue* CRValue_equals(CRValue* self, CRValue* other);
inline CRValue* CRValue_notEquals(CRValue* self, CRValue* other);

CRValue* CRString_new(const char* value, bool allocated);
CRValue* CRString_newCopy(const char* value, size_t length);
static void CRString_destroyValue(CRValue* self);
/**
 * Borrows a pointer to the string contents. The pointer has the same lifetime
 * of this object.
*/
inline const char* CRValue_asString(CRValue* self);

CRValue* CRTuple_new(CRValue* first, CRValue* second);
static void CRTuple_destroyValue(CRValue* self);
/**
 * Borrows a pointer to the tuple contents. The pointer has the same lifetime
 * of this object.
*/
static inline const CRTuple* CRValue_asTuple(CRValue* self);
inline CRValue* CRTuple_getFirst(CRValue* self);
inline CRValue* CRTuple_getSecond(CRValue* self);


CRValue* CRFunction_call(CRValue* self, ...);


#endif