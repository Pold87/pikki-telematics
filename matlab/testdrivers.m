drivers = dir('../drivers');
% drivers = dir('../drivers_small/1');
trips = 200;

workers = 4;

% map similarity count to probabilities
map = [.5, zeros(1, trips - 1)];
diff = .2;
for iter = 2 : trips - 1
    map(iter) = 1 - diff;
    diff = diff / 2;
end

drivercount = size(drivers, 1);
chunksize = floor(drivercount / workers);
tmp = struct2cell(drivers);

chunks{workers} = [];

for iter = 1 : workers - 1
    chunks{iter} = tmp(1 , (iter-1) * chunksize + 1 : iter * chunksize);
end

chunks{workers} = tmp(1 , (workers-1) * chunksize + 1 : end);

parfor iter = 1 : workers
    drivers2 = chunks{iter}';
    done = 0;
    for driver = 1 : length(drivers2)
        if strcmp(drivers2{driver}, '.') || strcmp(drivers2{driver}, '..')
            continue; 
        end
        probs = matchtrip(['../drivers/' drivers2{driver} '/'], map);
        for trip = 1 : trips
            probs(trip);
            
            fid = fopen('test1.csv', 'a+');
            fprintf(fid, '%s_%d,%f\n', drivers2{driver}, trip, probs(trip));
            fclose(fid);
        end
        fprintf('%d : %f %% done\n', iter, done/chunksize);
    end 
end

% parfor driver = drivers'
% %     ['../drivers/ | ' driver.name ' | /']
%     if strcmp(driver.name, '.') || strcmp(driver.name, '..')
%         continue; 
%     end
%     probs = matchtrip(['../drivers/' driver.name '/'], map);
%     driver.name
%     for trip = 1 : trips
%         probs(trip);
%         
%         fprintf(fid, '%s_%d,%f\n', driver.name, trip, probs(trip));
%     end
%     break;
% end
