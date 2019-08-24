switzerland = switzerland.name.str.replace(r'^dorf$|^dorf-|^dorf\s','')

### MYSQL - Cleaning ###
"""SELECT * FROM sbs_classification WHERE country='switzerland' and name REGEXP '^dorf$' or name REGEXP '^dorf ' or name REGEXP '^dorf-'""";