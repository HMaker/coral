#include <string.h>
#include "runtime.h"


CRObject* CRString_new(const char* value, bool owner) {
    CRObject* obj = CRObject_new();
    CRString* container = (CRString*) calloc(1, sizeof(CRString));
    if (container == NULL) {
        CR_ABORT("FATAL: CRValue_newString: failed to allocate a new CRString!\n");
        return NULL;
    }
    container->value = value;
    container->length = strlen(value);
    container->owner = owner;
    obj->_type = CR_STR;
    obj->value = container;
    return obj;
}


CRObject* CRString_newCopy(const char* value, size_t length) {
    CRObject* obj = CRObject_new();
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
    memcpy(copy, value, length + 1);
    container->value = copy;
    container->length = length;
    container->owner = true;
    obj->_type = CR_STR;
    obj->value = container;
    return obj;
}


void CRString_destroy(CRString* self) {
    if (self == NULL) return;
    if (self->owner && self->value != NULL) {
        free((void*)(self->value));
        self->value = NULL;
    }
    free(self);
}


CRObject* CRString_concat(CRObject* self, CRObject* other) {
    CRType selftype = CRObject_getType(self);
    CRType othertype = CRObject_getType(other);
    if (selftype == CR_STR && othertype == CR_STR) {
        const CRString* left = self->value;
        const CRString* right = other->value;
        char* result = malloc(left->length + right->length + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRString_concat: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, left->value, left->length);
        memcpy(result + left->length, right->value, right->length);
        return CRString_new(result, true);
    }
    if (selftype == CR_STR) {
        const CRString* left = self->value;
        int64_t right = CRObject_asInt(other);
        char rightstr[21];
        int written = snprintf(rightstr, sizeof(rightstr), "%ld", right);
        if (written <= 0) {
            CR_ABORT("FATAL: CRString_concat: snprintf failed with %d\n", written);
            return NULL;
        }
        size_t rightlen = written;
        char* result = malloc(left->length + rightlen + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRString_concat: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, left->value, left->length);
        memcpy(result + left->length, rightstr, rightlen + 1);
        return CRString_new(result, true);
    } else {
        const CRString* right = other->value;
        int64_t left = CRObject_asInt(self);
        char leftstr[21];
        int written = snprintf(leftstr, sizeof(leftstr), "%ld", left);
        if (written <= 0) {
            CR_ABORT("FATAL: CRString_concat: snprintf failed with %d\n", written);
            return NULL;
        }
        size_t leftlen = written;
        char* result = malloc(leftlen + right->length + 1);
        if (result == NULL) {
            CR_ABORT("FATAL: CRString_concat: failed to allocate new string!");
            return NULL;
        }
        memcpy(result, leftstr, leftlen);
        memcpy(result + leftlen, right->value, right->length + 1);
        return CRString_new(result, true);
    }
}


CRObject* CRString_equals(CRString* self, CRString* other) {
    if (self->length != other->length) {
        return CRObject_newBool(false);
    }
    return CRObject_newBool(strcmp(self->value, other->value));
}


CRObject* CRString_repr(CRString* self) {
    // " + self->value + " + null terminator
    char* repr = malloc(1 + self->length + 1 + 1);
    if (repr == NULL) {
        CR_ABORT("FATAL: CRString_repr: failed to allocate new buffer\n");
        return NULL;
    }
    memcpy(repr, "\"", 1);
    memcpy(repr + 1, self->value, self->length);
    memcpy(repr + (1 + self->length), "\"", 2); // copy nullbyte
    return CRString_new(repr, true);
}
