function res_aux = connect_function(sc,patient,hardwareN,hardware,rep,bck_meals,bck_meal_announce,bck_SQinsulin,ind)

save('scpython.mat','sc')
hardware=load_hardware(hardwareN,hardware);

save hardware

Lstruttura=load_subject(patient);

save Lstruttura

struttura = Lstruttura;

%seed=sum(100*clock);
seed = 1000;
struttura.rg=RandStream.create('mrg32k3a','NumStreams',1,'StreamIndices',1,'Seed',seed);

hd = hardware;

res_aux = run_simulation(sc,struttura,hd,rep,bck_meals,bck_meal_announce,bck_SQinsulin,ind);




