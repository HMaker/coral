#include <string.h>
#include "runtime.h"


CRObject* CRTuple_new(CRObject* first, CRObject* second) {
    CRObject* obj = CRObject_new();
    CRTuple* tuple = (CRTuple*) calloc(1, sizeof(CRTuple));
    if (tuple == NULL) {
        CR_ABORT("FATAL: CRTuple_new: failed to allocate a new CRTuple!\n");
        return NULL;
    }
    tuple->first = first;
    tuple->second = second;
    obj->_type = CR_TUPLE;
    obj->value = tuple;
    CRObject_incref(first);
    CRObject_incref(second);
    return obj;
}

void CRTuple_destroy(CRTuple* self) {
    if (self == NULL) return;
    CRObject_decref(self->first);
    CRObject_decref(self->second);
    free(self);
}


CRObject* CRTuple_getFirst(CRObject* self) {
    return CRObject_asTuple(self)->first;
}

CRObject* CRTuple_getSecond(CRObject* self) {
    return CRObject_asTuple(self)->second;
}


CRObject* CRTuple_repr(CRTuple* self) {
    // recursive tuples will cause stack overflow
    CRObject* first = CRObject_getTypeRepr(self->first);
    CRObject* second = CRObject_getTypeRepr(self->second);
    CRString* firststr = first->value;
    CRString* secondstr = second->value;
    // "(" + firststr->value + ", " + secondstr->value + ")" + null terminator
    char* repr = malloc(1 + firststr->length + 2 + secondstr->length + 1);
    if (repr == NULL) {
        CR_ABORT("FATAL: CRTuple_repr: failed to allocate new buffer\n");
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
    CRObject* result = CRString_new(repr, true);
    CRObject_decref(first);
    CRObject_decref(second);
    return result;
}
