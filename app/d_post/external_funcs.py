from datetime import datetime
from myapp.models import Registers2
from datetime import date


def getTupleOfMissingRegistries():
    '''Returns a list of skipped registries for the current and previous years
     in the format (registry id, registry number)'''
    this_year = date.today().year
    prev_year = this_year - 1
    qs_this_year = Registers2.objects.filter(reg_date__year=this_year)
    qs_prev_year = Registers2.objects.filter(reg_date__year=prev_year)
    list_of_all_regs_this_year = list(range(max( list(qs_this_year.values_list('reg_number', flat=True)) ))) 
    list_of_all_regs_prev_year = list(range(max( list(qs_prev_year.values_list('reg_number', flat=True)) ))) 
    list_of_used_regs_this_year = list(qs_this_year.values_list('reg_number', flat=True))
    list_of_used_regs_prev_year = list(qs_prev_year.values_list('reg_number', flat=True))
    list_of_missing_regs_this_year = list(set(list_of_all_regs_this_year)-set(list_of_used_regs_this_year))
    list_of_missing_regs_prev_year = list(set(list_of_all_regs_prev_year)-set(list_of_used_regs_prev_year))
    list_of_missing_regs_this_year.sort()
    list_of_missing_regs_prev_year.sort()
    result_prev_year = [tuple([str(prev_year)+'/'+str(x), str(prev_year)+'/'+str(x)]) for x in list_of_missing_regs_prev_year]
    result_this_year = [tuple([str(this_year)+'/'+str(x), str(this_year)+'/'+str(x)]) for x in list_of_missing_regs_this_year]
    result = result_prev_year + result_this_year
    result.sort(reverse=True)
    # insert 'новый' at the begining of list
    result.insert(0, ('новый', 'новый'))
    return result
